// app.js

document.addEventListener('DOMContentLoaded', () => {
    // 获取 DOM 元素
    const generateForm = document.getElementById('generateForm');
    const promptInput = document.getElementById('promptInput');
    const imageUpload = document.getElementById('imageUpload');
    const apiKeyInput = document.getElementById('apiKeyInput');
    const historyList = document.getElementById('history-list');
    const generateBtn = document.getElementById('generateBtn');

    // 基础配置
    const API_BASE_URL = '/api'; // 或者你的公网IP:端口

    // 辅助函数：渲染单个历史记录项
    const renderHistoryItem = (item) => {
        const li = document.createElement('li');
        li.className = 'list-group-item';

        let videoPlayerHtml = '';
        if (item.video_url) {
            // 使用 <video> 标签作为默认播放器
            videoPlayerHtml = `
                <div class="video-preview-container" style="width: 200px;">
                    <video controls muted autoplay style="width: 100%;" src="${API_BASE_URL}${item.video_url}"></video>
                </div>
            `;
        } else {
            videoPlayerHtml = `<div class="video-preview-container" style="width: 200px;">视频生成中...</div>`;
        }

        let statusClass = 'badge bg-secondary';
        if (item.status === '文生视频' || item.status === '图生视频') {
            statusClass = 'badge bg-success';
        } else if (item.status === '生成失败') {
            statusClass = 'badge bg-danger';
        } else if (item.status === '生成中') {
            statusClass = 'badge bg-warning text-dark';
        }

        li.innerHTML = `
            <div class="d-flex align-items-center flex-grow-1">
                <div class="me-3">
                    ${videoPlayerHtml}
                </div>
                <div class="flex-grow-1">
                    <p class="mb-1 text-muted small">${item.start_time}</p>
                    <p class="mb-1"><strong>提示词:</strong> ${item.prompt}</p>
                    <span class="${statusClass}">${item.status}</span>
                    <span class="badge bg-info text-dark ms-2">用时: ${item.duration ? item.duration : '...'}</span>
                    <span class="badge bg-primary ms-2">${item.mode}</span>
                </div>
            </div>
            <div class="ms-3 d-flex flex-column align-items-end">
                <div class="mb-2">
                    <button class="btn btn-sm btn-outline-secondary copy-prompt-btn" data-prompt="${item.prompt}">
                        复制提示词
                    </button>
                    ${item.video_url ? `<a href="${API_BASE_URL}${item.video_url}" download class="btn btn-sm btn-outline-success ms-2">下载视频</a>` : ''}
                </div>
                <div class="text-muted small">ID: ${item.task_id.substring(0, 8)}...</div>
            </div>
        `;
        historyList.prepend(li);
        
        // 为复制按钮添加事件监听器
        li.querySelector('.copy-prompt-btn').addEventListener('click', (e) => {
            const prompt = e.target.getAttribute('data-prompt');
            navigator.clipboard.writeText(prompt)
                .then(() => alert('提示词已复制！'))
                .catch(err => console.error('复制失败', err));
        });
    };

    // 函数：获取并渲染历史记录
    const fetchAndRenderHistory = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/history`);
            const history = await response.json();
            historyList.innerHTML = ''; // 清空现有列表
            history.forEach(item => renderHistoryItem(item));
        } catch (error) {
            console.error('获取历史记录失败:', error);
        }
    };

    // 函数：轮询任务状态
    const pollTaskStatus = (taskId, startTime) => {
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/status/${taskId}`);
                if (response.status === 404) {
                    console.warn(`任务 ${taskId} 未找到，停止轮询。`);
                    clearInterval(pollInterval);
                    return;
                }
                const data = await response.json();
                
                // 找到并更新历史记录
                const historyItems = document.querySelectorAll('#history-list .list-group-item');
                historyItems.forEach(item => {
                    if (item.querySelector('.text-muted.small').textContent.includes(taskId.substring(0, 8))) {
                        // 更新状态和用时
                        const statusBadge = item.querySelector('.badge.bg-warning');
                        if (statusBadge) {
                             statusBadge.textContent = data.status;
                             if (data.status === '生成中') {
                                statusBadge.classList.replace('bg-warning', 'bg-warning');
                             } else if (data.status === '成功' || data.status === '文生视频' || data.status === '图生视频') {
                                statusBadge.classList.replace('bg-warning', 'bg-success');
                             } else if (data.status === '生成失败') {
                                statusBadge.classList.replace('bg-warning', 'bg-danger');
                             }
                        }
                        const durationBadge = item.querySelector('.badge.bg-info');
                        if (durationBadge) {
                            const elapsedTime = (Date.now() - startTime) / 1000;
                            durationBadge.textContent = `用时: ${elapsedTime.toFixed(2)}s`;
                        }

                        // 如果任务完成（成功或失败），则更新完整项并停止轮询
                        if (data.status !== '生成中') {
                            clearInterval(pollInterval);
                            fetchAndRenderHistory(); // 重新加载整个列表以确保数据同步
                        }
                    }
                });

            } catch (error) {
                console.error('轮询任务状态失败:', error);
                clearInterval(pollInterval); // 失败时停止轮询
                // 可以在这里更新UI为“生成失败”
                const historyItems = document.querySelectorAll('#history-list .list-group-item');
                historyItems.forEach(item => {
                    if (item.querySelector('.text-muted.small').textContent.includes(taskId.substring(0, 8))) {
                        item.querySelector('.badge.bg-warning').textContent = '生成失败';
                        item.querySelector('.badge.bg-warning').classList.replace('bg-warning', 'bg-danger');
                    }
                });
            }
        }, 3000); // 每3秒轮询一次
    };


    // 监听表单提交事件
    generateForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // 阻止表单默认提交行为

        generateBtn.disabled = true;
        generateBtn.textContent = '生成中...';

        const prompt = promptInput.value;
        const imageFile = imageUpload.files[0];
        const apiKey = apiKeyInput.value.trim();

        if (!prompt) {
            alert('请输入提示词！');
            generateBtn.disabled = false;
            generateBtn.textContent = '开始生成';
            return;
        }

        let imageUrl = null;
        try {
            if (imageFile) {
                // 上传图片
                const formData = new FormData();
                formData.append('image', imageFile);
                const uploadResponse = await fetch(`${API_BASE_URL}/upload_image`, {
                    method: 'POST',
                    body: formData
                });
                const uploadData = await uploadResponse.json();
                if (uploadData.error) {
                    throw new Error(uploadData.error);
                }
                imageUrl = `${API_BASE_URL}${uploadData.image_url}`;
            }

            // 提交生成任务到后端
            const generateResponse = await fetch(`${API_BASE_URL}/generate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt: prompt,
                    image_url: imageUrl,
                    api_key: apiKey
                })
            });
            const generateData = await generateResponse.json();

            if (generateData.error) {
                throw new Error(generateData.error);
            }

            // 立即渲染一个“生成中”的历史记录项
            const newItem = {
                task_id: generateData.task_id,
                start_time: new Date().toLocaleTimeString(),
                prompt: prompt,
                status: '生成中',
                video_url: null,
                image_url: imageUrl,
                duration: null,
                mode: imageUrl ? '图生视频' : '文生视频'
            };
            renderHistoryItem(newItem);

            // 开始轮询任务状态
            const startTime = Date.now();
            pollTaskStatus(generateData.task_id, startTime);

        } catch (error) {
            alert(`生成视频失败: ${error.message}`);
            console.error('生成视频失败:', error);
        } finally {
            generateBtn.disabled = false;
            generateBtn.textContent = '开始生成';
        }
    });

    // 页面加载时获取历史记录
    fetchAndRenderHistory();
});