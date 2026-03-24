# API Reference

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

# Start server
await server.start()

# Stop server
await server.stop()
```

## Logger

```python
from ncorn.logging import logger

logger.info("Message")
logger.warning("Message")
logger.error("Message")
logger.success("Message")
```
