# video_processor.py

import os
import time
import json
import uuid
import concurrent.futures
from datetime import datetime
import threading
import markdown

# 严格遵循MVP的SDK导入方式
from google import genai
from google.genai import types
from google.genai.types import Image

# 导入历史记录管理模块
import history_manager

# --- 配置 ---
SAVE_VIDEO_PATH = 'videos'
SAVE_IMAGE_PATH = 'images'
NEGATIVE_PROMPT = os.getenv('NEGATIVE_PROMPT', '')
SLEEP_TIME = int(os.getenv('SLEEP_TIME') or 10)
LOGS_PATH = 'logs'

# --- 线程池和任务状态字典 ---
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)
task_status_cache = {}

# --- 辅助函数 ---
def create_task_log(task_id, content):
    """
    将内容以Markdown格式写入任务日志文件。
    """
    log_dir = os.path.join(LOGS_PATH, task_id)
    os.makedirs(log_dir, exist_ok=True)
    log_file_path = os.path.join(log_dir, 'log.md')
    
    with open(log_file_path, 'a', encoding='utf-8') as f:
        f.write(content + '\n')

def process_video_generation(task_id, prompt, local_image_path, api_key):
    """
    在后台线程中执行视频生成任务。
    严格遵循MVP的SDK调用模式，并包含日志和错误处理。
    """
    start_time = time.time()
    
    task_status_cache[task_id] = {
        'status': '生成中', 
        'progress': '...',
        'elapsed_time': '0.00s'
    }
    create_task_log(task_id, f"# 任务开始：{datetime.now()}\n\n- **任务ID:** `{task_id}`\n- **提示词:** {prompt}\n- **模式:** {'图生视频' if local_image_path else '文生视频'}\n")

    try:
        client = genai.Client(api_key=api_key)
        
        generate_videos_kwargs = {
            'model': "veo-3.0-generate-preview",
            'prompt': prompt,
        }
        
        if NEGATIVE_PROMPT:
            generate_videos_kwargs['config'] = types.GenerateVideosConfig(negative_prompt=NEGATIVE_PROMPT)
        if local_image_path:
            generate_videos_kwargs['image'] = types.Image.from_file(location=local_image_path)
            
        create_task_log(task_id, f"## API 调用\n\n- **调用时间:** {datetime.now()}\n- **API参数:**\n```json\n{json.dumps(generate_videos_kwargs, default=str, indent=2)}\n```\n")
        
        operation = client.models.generate_videos(**generate_videos_kwargs)

        timeout_seconds = 600
        while not operation.done:
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout_seconds:
                raise TimeoutError("视频生成请求超时。")
            
            create_task_log(task_id, f"## 状态轮询\n\n- **时间:** {datetime.now()}\n- **状态:** `生成中`\n- **已用时:** {elapsed_time:.2f}s\n")
            
            time.sleep(SLEEP_TIME)
            operation = client.operations.get(operation)

        if not getattr(operation, "response", None) or not getattr(operation.response, "generated_videos", None):
            error_details = getattr(operation, "error", None) or "API返回结果为空或不包含视频URL。"
            raise Exception(f"API返回错误或空响应: {error_details}")

        generated_video = operation.response.generated_videos[0]
        
        video_filename = f"{uuid.uuid4()}.mp4"
        video_filepath = os.path.join(SAVE_VIDEO_PATH, video_filename)
        
        # 修正视频保存逻辑
        if getattr(generated_video.video, "video_bytes", None):
            with open(video_filepath, 'wb') as f:
                f.write(generated_video.video.video_bytes)
        elif getattr(generated_video.video, "uri", None):
            downloaded_bytes = client.files.download(file=generated_video.video)
            if not isinstance(downloaded_bytes, bytes):
                 raise Exception("下载的不是视频字节流。")
            with open(video_filepath, 'wb') as f:
                f.write(downloaded_bytes)
        else:
            raise Exception("API返回的视频数据既无bytes也无uri。")
        
        local_video_url = f'/videos/{video_filename}'
        end_time = time.time()
        duration = f'{end_time - start_time:.2f}s'
        
        status_mode = '图生视频' if local_image_path else '文生视频'
        history_manager.update_history_status(task_id, status_mode, local_video_url, duration)
        
        task_status_cache[task_id] = {
            'status': status_mode, 
            'video_url': local_video_url, 
            'duration': duration,
            'elapsed_time': duration
        }
        
        create_task_log(task_id, f"## 任务完成：{datetime.now()}\n\n- **最终状态:** `成功`\n- **用时:** {duration}\n- **视频URL:** {local_video_url}\n")
        
    except Exception as e:
        end_time = time.time()
        elapsed_time = f'{end_time - start_time:.2f}s'
        error_message = f"视频生成失败: {e}"
        print(f"[{datetime.now()}] 任务 {task_id}: {error_message}")
        history_manager.update_history_status(task_id, '生成失败', duration=elapsed_time)
        task_status_cache[task_id] = {
            'status': '生成失败', 
            'error': error_message,
            'elapsed_time': elapsed_time
        }
        create_task_log(task_id, f"## 任务失败：{datetime.now()}\n\n- **最终状态:** `失败`\n- **错误信息:** {error_message}\n- **用时:** {elapsed_time}\n")
    finally:
        if task_id in task_status_cache:
            del task_status_cache[task_id]

def submit_generation_task(task_id, prompt, local_image_path, api_key):
    executor.submit(process_video_generation, task_id, prompt, local_image_path, api_key)
    
def get_task_status(task_id):
    return task_status_cache.get(task_id, None)