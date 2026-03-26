# Деплой

Это руководство охватывает различные варианты развёртывания ncorn.

## Чеклист для продакшена

Перед развёртыванием в продакшене:

1. ✅ Используйте SSL/TLS сертификаты
2. ✅ Установите соответствующие таймауты
3. ✅ Настройте rate limiting
4. ✅ Используйте несколько воркеров
5. ✅ Настройте логирование и мониторинг
6. ✅ Настройте health checks

## Базовый деплой для продакшена

```bash
ncorn app:app --host 0.0.0.0 --port 443 \
  --ssl-keyfile /path/to/key.pem \
  --ssl-certfile /path/to/cert.pem \
  --workers 4 \
  --rate-limit 100 \
  --rate-limit-window 60
```

## Деплой с несколькими воркерами

Для лучшей производительности используйте несколько воркеров:

```bash
ncorn app:app --workers 4
```

Каждый воркер:
- Запускается в отдельном процессе
- Обрабатывает запросы независимо
- Использует тот же порт

## За reverse proxy

Хотя ncorn имеет нативную поддержку SSL, вы также можете запустить за nginx:

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

## Управление процессами

### Systemd

Создайте `/etc/systemd/system/ncorn.service`:

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

Затем:

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

## SSL сертификаты

### Самоподписанные (для разработки)

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

### Let's Encrypt (для продакшена)

Используйте certbot:

```bash
certbot certonly --standalone -d example.com
```

Затем настройте ncorn:

```bash
ncorn app:app \
  --ssl-keyfile /etc/letsencrypt/live/example.com/privkey.pem \
  --ssl-certfile /etc/letsencrypt/live/example.com/fullchain.pem
```

## Health Checks

Для балансировщиков нагрузки и оркестраторов:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "healthy"}
```

## Оптимизация производительности

### Количество воркеров

Хорошей отправной точкой будет 2-4 воркера на ядро CPU:

```bash
ncorn app:app --workers $(nproc)
```

### Таймауты

Настройте под ваше приложение:

```bash
ncorn app:app \
  --header-timeout 30 \
  --body-timeout 60 \
  --keepalive-timeout 5
```

### Лимиты соединений

```bash
ncorn app:app \
  --max-connections 1000 \
  --max-connections-per-ip 50
```
