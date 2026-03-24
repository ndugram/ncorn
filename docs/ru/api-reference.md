# Справка по API

## Config

```python
from ncorn.config import Config

config = Config(
    host="127.0.0.1",
    port=8000,
    workers=1,
    reload=False,
    max_body_size=16777216,
    header_timeout=30.0,
    body_timeout=60.0,
    keepalive_timeout=5.0,
    max_headers=100,
    max_keepalive_requests=100,
    rate_limit_requests=100,
    rate_limit_window=60.0,
)
```

## HTTPServer

```python
from ncorn.server import HTTPServer
from ncorn.config import Config
from myapp import app

config = Config(host="0.0.0.0", port=8080)
server = HTTPServer(app, config)

# Запуск сервера
await server.start()

# Остановка сервера
await server.stop()
```

## Logger

```python
from ncorn.logging import logger

logger.info("Сообщение")
logger.warning("Сообщение")
logger.error("Сообщение")
logger.success("Сообщение")
```
