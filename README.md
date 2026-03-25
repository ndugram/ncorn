<p align="center">
  <img src="https://ncorn.readthedocs.io/en/latest/logo.png" style="background:white; padding:12px; border-radius:10px; width:350">
</p>

<div align="center">

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://pypi.org/project/ncorn/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

## Features

- **Fast Performance** - Built on asyncio for high performance
- **ASGI Compatible** - Full ASGI interface support for FastAPI
- **Production Ready** - Rate limiting, request validation, slowloris protection
- **Multi-Worker** - Support for multiple worker processes
- **Auto-Reload** - Development mode with file watching
- **Clean Logging** - Beautiful uvicorn-style console output
- **Security** - Header validation, body size limits, IP rate limiting

## Security Features

- **Max Body Size** - Limits request body to prevent DoS attacks
- **Header Validation** - Validates HTTP headers and rejects invalid requests
- **Slowloris Protection** - Timeout for header and body reads
- **IP Rate Limiting** - Limits requests per IP address

## Installation

```bash
pip install ncorn
```

## Quick Start

```bash
ncorn example_app:app
```

With custom host and port:

```bash
ncorn example_app:app --host 0.0.0.0 --port 8080
```

Multiple workers:

```bash
ncorn example_app:app --workers 4
```

Auto-reload on file changes:

```bash
ncorn example_app:app --reload
```

## Configuration

Create a config file:

```bash
ncorn config
```

This creates `ncorn.json` with default settings. You can edit this file and ncorn will use these settings by default.

Example configuration:

```json
{
  "host": "127.0.0.1",
  "port": 8000,
  "workers": 1,
  "reload": false,
  "max_body_size": 16777216,
  "max_header_size": 8192,
  "max_headers_total_size": 65536,
  "header_timeout": 30.0,
  "body_timeout": 60.0,
  "request_timeout": 10.0,
  "response_timeout": 10.0,
  "keepalive_timeout": 5.0,
  "keepalive_requests": 100,
  "max_headers": 100,
  "max_connections": 1000,
  "max_connections_per_ip": 50,
  "rate_limit_requests": 100,
  "rate_limit_window": 60.0,
  "write_buffer_limit": 65536,
  "drain_timeout": 1.0,
  "ip_whitelist": [],
  "ip_blacklist": [],
  "enable_security_headers": true,
  "waf_max_query_length": 4096
}
```

Command line options override config file settings.

## Example FastAPI App

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Example App")

class Item(BaseModel):
    name: str
    price: float
    tax: float | None = None

@app.get("/")
async def root():
    return {"message": "Hello from ncorn!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/items")
async def create_item(item: Item):
    total = item.price + (item.tax or 0)
    return {"name": item.name, "total": total}
```

Run it:

```bash
ncorn example_app:app
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
