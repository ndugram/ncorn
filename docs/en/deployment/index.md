# Deployment

This guide covers various deployment options for ncorn.

## Production Checklist

Before deploying to production:

1. ✅ Use SSL/TLS certificates
2. ✅ Set appropriate timeouts
3. ✅ Configure rate limiting
4. ✅ Use multiple workers
5. ✅ Set up logging and monitoring
6. ✅ Configure health checks

## Basic Production Deployment

```bash
ncorn app:app --host 0.0.0.0 --port 443 \
  --ssl-keyfile /path/to/key.pem \
  --ssl-certfile /path/to/cert.pem \
  --workers 4 \
  --rate-limit 100 \
  --rate-limit-window 60
```

## Multi-Worker Deployment

For better performance, use multiple workers:

```bash
ncorn app:app --workers 4
```

Each worker:
- Runs in a separate process
- Handles requests independently
- Shares the same port

## Behind Reverse Proxy

While ncorn has native SSL support, you can also run behind nginx:

```nginx
server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Process Management

### Systemd

Create `/etc/systemd/system/ncorn.service`:

```ini
[Unit]
Description=ncorn ASGI server
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/ncorn app:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl enable ncorn
sudo systemctl start ncorn
```

### Supervisor

```ini
[program:ncorn]
command=/usr/bin/ncorn app:app --host 0.0.0.0 --port 8000 --workers 4
directory=/path/to/project
user=www-data
autostart=true
autorestart=true
```

## SSL Certificates

### Self-Signed (Development)

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

### Let's Encrypt (Production)

Use certbot:

```bash
certbot certonly --standalone -d example.com
```

Then configure ncorn:

```bash
ncorn app:app \
  --ssl-keyfile /etc/letsencrypt/live/example.com/privkey.pem \
  --ssl-certfile /etc/letsencrypt/live/example.com/fullchain.pem
```

## Health Checks

For load balancers and orchestrators:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## Performance Tuning

### Worker Count

A good starting point is 2-4 workers per CPU core:

```bash
ncorn app:app --workers $(nproc)
```

### Timeouts

Adjust based on your application:

```bash
ncorn app:app \
  --header-timeout 30 \
  --body-timeout 60 \
  --keepalive-timeout 5
```

### Connection Limits

```bash
ncorn app:app \
  --max-connections 1000 \
  --max-connections-per-ip 50
```
