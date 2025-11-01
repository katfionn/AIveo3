# history_manager.py

import os
import json
import uuid
from datetime import datetime

# 历史记录文件路径
HISTORY_FILE = 'histories/history.json'

def save_history(data):
    """
    将新的历史记录条目保存到JSON文件。
    如果文件不存在，则会创建。
    """
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    if not os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f, ensure_ascii=False, indent=2)

    with open(HISTORY_FILE, 'r+', encoding='utf-8') as f:
        try:
            history = json.load(f)
        except json.JSONDecodeError:
            history = []
        history.insert(0, data)
        f.seek(0)
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_history():
    """
    从JSON文件加载所有历史记录。
    如果文件不存在，则返回一个空列表。
    """
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def update_history_status(task_id, status, video_url=None, duration=None):
    """
    根据任务ID更新历史记录的状态。
    """
    history = load_history()
    updated = False
    for item in history:
        if item['task_id'] == task_id:
            item['status'] = status
            if video_url:
                item['video_url'] = video_url
            if duration:
                item['duration'] = duration
            updated = True
            break
    
    if updated:
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)