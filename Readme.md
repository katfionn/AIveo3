<div align="center">
  <h1>AIVeo3 MVP Demo</h1>
  <a href="https://github.com/katfionn/AIveo3/blob/main/Readme_chs.md" style="font-size:24px;">中文版</a>
  <br><br>
  <img src="https://github.com/katfionn/AIveo3/blob/main/AIveo3_Logo.png?raw=true" alt="LOGO" width="300">
</div>


# Introduction
This is a simple MVP demo about connecting orginal API from google from worldwide but still follow it's policy. If you want to try to generate videos with Google Veo3, this project should be your best practice to start.
> It's...the best i can tell...u need to try the details about it and...keep your mouth shut...don't brag

For this version(there will be no futher update😛😜😝), it can do:
1. text to video
2. image and text to video
3. no more
# How to use

Andthe bugs in this version:
1. The generate order may not sync the real status after you submit it, you will need to refreash the page to see it. And also may not sync the result...so you need to....
2. The time generation cost, is not showing real time
I'm happy anyone can solve this, I can't solve it...
This is a tricky part, it's only fit for Linux, and if you don't know anything about it......just follow the leads(or you can just ask Gemini🤣🤣🤣)

## First
It's the most important step, you need to prepare two server(if you are in State...forget this part), and at least of it need to be in the US, it's for the backend program.

## Second
Download o Git clone codes to your server

## Third
Deal with the backend first. Use command tools get into the backend's dir, then run the command below
```
pip install -r requirements.txt
```
The `requirements.txt` is generated automatically, if it pop out sng warning, don't worry about it(only if tells you already have dependencies o your network connect is failed), just keep going, we can test it later.

## Forth
Get your api key from google cloud(u can learn form google), then paste it to the first key `GOOGLE_API_KEY` in the `config.json`, the file will let u know where you need to paste it.

## Fifth
Run the app.py in the command line，if it goes well, then goto next step. If it goes wrong...check the "Third" step, if it's still not work, as the Gemini please...🙊🙈🙈

## Sixth
Make sure your Linux or your server is opened and listening on port 5000(you can change it in `app.py` file)

## Seventh
Keep the command line in step "Fifth" running, then deploy the frontend. I use the openresty(some sub version of Nginx), the key is to write a reverse proxy to your backend(which means the app.py we talk in step "Fifth"). Here is my whole config in the openresty(include the reverse proxy), and i deploy it with 1panel(highly recommand). You will need to replace these config wo your own :`server_name`, `access_log`, `error_log`, `  location /api/`, `proxy_pass`, `root`, `ssl_trusted_certificate`.
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
        proxy_pass http://your_server_ip_or_domain:5000/; 
        proxy_set_header Host $host; 
        proxy_set_header X-Real-IP $remote_addr; 
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; 
        proxy_set_header X-Forwarded-Proto $scheme; 
    }
    add_header 'Access-Control-Allow-Origin' 'http://your_server_ip_or_domain:5000' always; 
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS'; 
    root /www/sites/veo3/index; 
    ssl_trusted_certificate /www/sites/veo3/ssl/fullchain.pem; 
}
```
> If you use 1panel like me, all you need to do paste and alternate is the `# 后端API反向代理` part

My site is not support HTTPs, so you need to figure it your own if you want.

## Eighth
Start the site, see if it works. My package has few test and demo history file, if their shows up, then try to generate a video. After you generate a video, you should know this project runs successful. Then you can goto next step, otherwise...copy the oder id(they looks like this `0d084f96-3540-49e6-820c-ec9a56b804c6`) and check the log in the backend's dir `/log`, you will finout what happends.

## Ninth
Kill the command line process we build in the step "Fifth". Alternate the system service in the `system service` folder, you need to change these to your real configs: `WorkingDirectory`, `ExecStart`. Then put the file to this directory `/etc/systemd/system/` (my system is Debian, so it goes here, u may need to google your own OS about it).

## Tenth
Run commands below one by one:
```
systemctl daemon-reload
```
```
systemctl start video-generator.service
```
```
systemctl status video-generator.service
```
By now, you can see a bunch of things, there will be some words show up green and before it have some words like "Active: ", then you know it works.

# Other thing...
- The service part is not have to be done, just can make it run all the time even after your machine reboot.
- If you find the file have some problem and seems nthing wrong, youcan try use tool like "dos2unix" convert all file to unix, because when i committ this on PC...so...
