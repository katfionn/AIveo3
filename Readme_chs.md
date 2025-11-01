<div align="center">
  <h1>AIVeo3 MVP 演示</h1>
  <a href="https://github.com/katfionn/AIveo3" style="font-size:24px;">English version</a>
  <br><br>
  <img src="https://github.com/katfionn/AIveo3/blob/main/AIveo3_Logo.png?raw=true" alt="LOGO" width="300">
</div>

# 简介
这是一个关于连接 Google 官方 API 的简单 MVP 演示项目，能从全球范围内使用，但依然遵守其政策。
> 这……已经是我能说的最好了……你需要自己体验细节，另外……嘴要严……别到处吹

本版本（不会再有后续更新😛😜😝）目前支持：
1. 文本转视频
2. 图片和文本转视频
3. 没有更多了

# 如何使用

本版本存在的 bug：
1. 生成的任务提交后，状态可能不同步，你需要手动刷新页面才能看到最新进度。同时结果也可能不同步……所以你需要……
2. 生成所需时间显示不是真实时间
如果谁能解决这些 bug，我会很高兴，我自己解决不了……
这个环节有点麻烦，只适合 Linux，如果你完全不懂……就按步骤操作（或者直接问 Gemini🤣🤣🤣）

## 第一步
这是最重要的一步，你需要准备两台服务器（如果你在美国……忽略这一步），至少有一台需要在美国，用于部署后端程序。

## 第二步
下载或 git clone 代码到你的服务器

## 第三步
先处理后端。用命令行进入 backend 目录，然后执行以下命令：
```
pip install -r requirements.txt
```
`requirements.txt` 文件是自动生成的，如果出现警告也不用担心（只要不是说你已经有依赖或者网络连接失败），先继续后面步骤，后续可以再测试。

## 第四步
去 Google Cloud 获取你的 API key（可以百度/谷歌学习），然后将其粘贴到 `config.json` 文件里第一个键 `GOOGLE_API_KEY`，具体文件会提示你该粘贴到哪里。

## 第五步
在命令行运行 `app.py`，如果一切正常，进入下一步。如果有报错……回去检查“第三步”，还不行就问 Gemini 吧🙊🙈🙈

## 第六步
确保你的 Linux 或服务器已经打开并监听 5000 端口（你可以在 `app.py` 文件中更改端口）

## 第七步
保持“第五步”命令行处于运行状态，然后部署前端。我用的是 openresty（nginx 的一个子版本），关键是写一个反向代理到你的后端（即“第五步”中说的 `app.py`）。下面是我在 openresty 下的完整配置（包括反代），我用 1panel 部署（强烈推荐）。你需要把这些配置替换成你自己的：`server_name`，`access_log`，`error_log`，`  location /api/`，`proxy_pass`，`root`，`ssl_trusted_certificate`。
```nginx
server {
    listen 80 ; 
    listen 30030 ; 
    listen 30300 ; 
    server_name replace me; 
    index index.php index.html index.htm default.php default.htm default.html; 
    proxy_set_header Host $host; 
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; 
    proxy_set_header X-Forwarded-Host $server_name; 
    proxy_set_header X-Real-IP $remote_addr; 
    proxy_http_version 1.1; 
    proxy_set_header Upgrade $http_upgrade; 
    proxy_set_header Connection "upgrade"; 
    access_log /www/sites/veo3/log/access.log; 
    error_log /www/sites/veo3/log/error.log; 
    location ^~ /.well-known/acme-challenge {
        allow all; 
        root /usr/share/nginx/html; 
    }
    # 后端API反向代理
    location /api/ {
        proxy_pass http://103.79.76.195:5000/; 
        proxy_set_header Host $host; 
        proxy_set_header X-Real-IP $remote_addr; 
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; 
        proxy_set_header X-Forwarded-Proto $scheme; 
    }
    add_header 'Access-Control-Allow-Origin' 'http://103.79.76.195:5000' always; 
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS'; 
    root /www/sites/veo3/index; 
    ssl_trusted_certificate /www/sites/veo3/ssl/fullchain.pem; 
}
```
> 如果你和我一样用 1panel，只需要粘贴并修改 `# 后端API反向代理` 相关内容即可。

我的站点不支持 HTTPS，如果你需要，请自行研究配置。

## 第八步
启动站点，看看是否正常运行。我的包里有几个测试和 demo 的历史文件，如果能正常显示，试着生成一个视频。如果视频生成成功，说明项目部署成功。否则……复制订单号（形如 `0d084f96-3540-49e6-820c-ec9a56b804c6`），去后端目录 `/log` 下查找日志，看看发生了什么。

## 第九步
杀掉“第五步”中运行的命令行进程。然后修改 `system service` 文件夹下的系统服务，需将其中的 `WorkingDirectory` 和 `ExecStart` 替换为你自己的配置。

## 第十步
依次运行以下命令：
```
systemctl daemon-reload
```
```
systemctl start video-generator.service
```
```
systemctl status video-generator.service
```
此时你会看到很多输出，如果有绿色的“Active: ”字样，就说明服务正常运行。

# 其他说明
- 系统服务部分不是必须，只是为了保证即使重启机器服务也能自动运行。
- 如果发现文件有莫名其妙的问题，可以尝试用 "dos2unix" 工具将所有文件转换为 unix 格式，因为我是用 Windows 提交的……
