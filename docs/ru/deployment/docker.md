# Docker

ncorn можно контейнеризировать с помощью Docker для удобного развёртывания.

## Базовый Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Установка ncorn
RUN pip install ncorn

# Копирование приложения
COPY . .

# Запуск ncorn
CMD ["ncorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Сборка и запуск

```bash
docker build -t ncorn-app .
docker run -d -p 8000:8000 --name myapp ncorn-app
```

## Docker с SSL

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install ncorn

COPY certs/ ./certs/
COPY app.py .

CMD ["ncorn", "app:app", "--host", "0.0.0.0", "--port", "443", \
     "--ssl-keyfile", "certs/key.pem", \
     "--ssl-certfile", "certs/cert.pem"]
```

## Мультистейдж сборка

Для меньших образов:

```dockerfile
# Стадия сборки
FROM python:3.11-slim as builder

WORKDIR /app
RUN pip install --user ncorn

# Рантайм стадия
FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY --from=builder /app /app

ENV PATH=/root/.local/bin:$PATH

CMD ["ncorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Docker Compose

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NCORN_HOST=0.0.0.0
      - NCORN_PORT=8000
    volumes:
      - .:/app

  # С SSL
  web-ssl:
    build: .
    ports:
      - "443:443"
    volumes:
      - ./certs:/app/certs:ro
    command: >
      ncorn app:app
      --host 0.0.0.0
      --port 443
      --ssl-keyfile certs/key.pem
      --ssl-certfile certs/cert.pem
```

## Docker для продакшена

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir ncorn

# Создание не-root пользователя
RUN useradd -m appuser
USER appuser

COPY --chown=appuser:appuser . .

EXPOSE 8000

CMD ["ncorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## Health Check

```yaml
services:
  web:
    build: .
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    ports:
      - "8000:8000"
```

## Kubernetes

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: ncorn-app
spec:
  containers:
  - name: web
    image: ncorn-app:latest
    ports:
    - containerPort: 8000
    env:
    - name: NCORN_HOST
      value: "0.0.0.0"
    - name: NCORN_PORT
      value: "8000"
    resources:
      limits:
        memory: "512Mi"
        cpu: "500m"
```

## Лучшие практики

1. **Используйте не-root пользователя** в контейнерах
2. **Установите правильные лимиты ресурсов**
3. **Используйте health checks**
4. **Включите SSL в продакшене**
5. **Используйте мультистейдж сборки** для меньших образов
6. **Не кэшируйте зависимости** в продакшене (`--no-cache-dir`)
