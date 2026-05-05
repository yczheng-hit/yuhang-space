# 生产部署指南（Linux 原生部署）

## 系统依赖

```bash
sudo apt update && sudo apt install -y python3.12 python3.12-venv \
    postgresql nginx certbot python3-certbot-nginx
```

## 部署步骤

### 1. 创建服务用户

```bash
sudo useradd -m -s /bin/bash yuhang
sudo su - yuhang
```

### 2. 克隆并安装

```bash
git clone <repo-url> ~/yuhang-space
cd ~/yuhang-space/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. 配置环境变量

```bash
cp ../.env.example ../.env
nano ../.env
```

关键配置项：
- `DATABASE_URL`: 生产数据库连接
- `JWT_SECRET_KEY`: 随机 64 位字符串
- `LLM_API_KEY`: 大模型 API Key
- `DEBUG=false`

### 4. 初始化数据库

```bash
sudo -u postgres createdb yuhang_space
alembic upgrade head
```

### 5. 构建前端

```bash
cd ~/yuhang-space/frontend
npm install
npm run build
```

### 6. 配置 systemd 服务

创建 `/etc/systemd/system/yuhang-space.service`：

```ini
[Unit]
Description=寰宇智杭后端 API
After=network.target postgresql.service

[Service]
Type=simple
User=yuhang
WorkingDirectory=/home/yuhang/yuhang-space/backend
ExecStart=/home/yuhang/yuhang-space/backend/.venv/bin/uvicorn \
    app.main:app \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 4
Restart=always
RestartSec=5
EnvironmentFile=/home/yuhang/yuhang-space/.env

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable yuhang-space
sudo systemctl start yuhang-space
```

### 7. 配置 Nginx

创建 `/etc/nginx/sites-available/yuhang-space`：

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        root /home/yuhang/yuhang-space/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_buffering off;
        proxy_cache off;
    }

    location /media/ {
        alias /home/yuhang/yuhang-space/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /api/v1/maintenance/ {
        deny all;
        return 403;
    }
}
```

启用站点并申请证书：

```bash
sudo ln -s /etc/nginx/sites-available/yuhang-space /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d your-domain.com
```
