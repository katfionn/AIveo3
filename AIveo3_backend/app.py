# app.py

import os
import json
import uuid
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# 导入我们新创建的模块
import history_manager
import video_processor

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# --- 配置 ---
if os.path.exists('config.json'):
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
else:
    config = {}

VEO_API_KEY = os.getenv('GOOGLE_API_KEY') or config.get('GOOGLE_API_KEY')
SAVE_VIDEO_PATH = os.getenv('SAVE_VIDEO_PATH') or config.get('SAVE_VIDEO_PATH', 'videos')
SAVE_IMAGE_PATH = os.getenv('SAVE_IMAGE_PATH') or config.get('SAVE_IMAGE_PATH', 'images')

# 确保保存路径存在
os.makedirs(SAVE_VIDEO_PATH, exist_ok=True)
os.makedirs(SAVE_IMAGE_PATH, exist_ok=True)

# --- API 路由 ---
@app.route('/generate', methods=['POST'])
def generate_video_route():
    data = request.json
    api_key = data.get('api_key') or VEO_API_KEY
    if not api_key:
        return jsonify({"error": "No API key provided"}), 400

    prompt = data.get('prompt')
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400

    image_url_from_frontend = data.get('image_url')
    local_image_path = None
    if image_url_from_frontend:
        filename = os.path.basename(image_url_from_frontend)
        local_image_path = os.path.join(SAVE_IMAGE_PATH, filename)
        if not os.path.exists(local_image_path):
            return jsonify({"error": "Uploaded image file not found on server."}), 404

    task_id = str(uuid.uuid4())
    start_time = datetime.now()
    history_item = {
        'task_id': task_id,
        'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
        'prompt': prompt,
        'status': '生成中',
        'video_url': None,
        'image_url': image_url_from_frontend,
        'duration': None,
        'mode': '图生视频' if image_url_from_frontend else '文生视频'
    }
    history_manager.save_history(history_item)

    video_processor.submit_generation_task(task_id, prompt, local_image_path, api_key)
    return jsonify({'task_id': task_id}), 200

@app.route('/status/<task_id>', methods=['GET'])
def get_status_route(task_id):
    status_data = video_processor.get_task_status(task_id)
    if status_data:
        return jsonify(status_data), 200
    
    history = history_manager.load_history()
    for item in history:
        if item['task_id'] == task_id:
            return jsonify({
                'status': item['status'],
                'video_url': item['video_url'],
                'duration': item['duration']
            }), 200

    return jsonify({"error": "Task not found"}), 404

@app.route('/upload_image', methods=['POST'])
def upload_image_route():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(SAVE_IMAGE_PATH, filename)
        file.save(filepath)
        return jsonify({'image_url': f'/images/{filename}'}), 200

@app.route('/history', methods=['GET'])
def get_history_route():
    history = history_manager.load_history()
    return jsonify(history), 200

@app.route('/images/<filename>', methods=['GET'])
def get_image_route(filename):
    return send_from_directory(SAVE_IMAGE_PATH, filename)

@app.route('/videos/<filename>', methods=['GET'])
def get_video_route(filename):
    return send_from_directory(SAVE_VIDEO_PATH, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)