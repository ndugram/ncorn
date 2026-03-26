# Welcome

![ncorn](logo.png)

_ncorn is a production-ready ASGI web server for FastAPI applications._

---

**Documentation**: [https://ncorn.ndugram.dev](https://ncorn.readthedocs.io/)

**Source Code**: [https://github.com/ndugram/ncorn](https://github.com/ndugram/ncorn)

---

**ncorn** is an ASGI web server implementation for Python, designed specifically for FastAPI applications.

Until recently Python has lacked a minimal low-level server/application interface for async frameworks. The [ASGI specification](https://asgi.readthedocs.io/en/latest/) fills this gap, and means we're now able to start building a common set of tooling usable across all async frameworks.

ncorn is built with a focus on **performance** and **production-readiness**, featuring built-in security measures and SSL/TLS support.

## Features

- **Fast Performance** - Built on asyncio for high performance
- **ASGI Compatible** - Full ASGI interface support for FastAPI
- **Production Ready** - Rate limiting, request validation, slowloris protection
- **SSL/TLS** - Native HTTPS support without reverse proxy
- **Multi-Worker** - Support for multiple worker processes
- **Auto-Reload** - Development mode with file watching
- **Clean Logging** - Beautiful uvicorn-style console output
- **Security** - Header validation, body size limits, IP rate limiting

## Quickstart

ncorn is available on PyPI so installation is as simple as:

```bash
pip install ncorn
```

Let's create a simple FastAPI application:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from ncorn!"}
```

Then we can run it with ncorn:

```bash
ncorn main:app
```

## Running with HTTPS

ncorn has built-in SSL/TLS support - no need for external reverse proxy:

```bash
ncorn main:app --ssl-keyfile certs/key.pem --ssl-certfile certs/cert.pem
```

This will start the server on `https://127.0.0.1:8000`

## Requirements

- Python 3.11+
- httptools
- rich
- annotated-doc

