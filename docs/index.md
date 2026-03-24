# ncorn

Production-ready ASGI web server designed specifically for FastAPI applications.

## Features

- Async TCP server using asyncio
- HTTP/1.1 parser using httptools
- ASGI adapter layer
- Middleware system (server-level)
- Request validation (headers, body size limits)
- Rate limiting
- Graceful shutdown
- Keep-alive connections

## Security Features

- Max body size limit
- Header validation
- Slowloris protection (timeouts)
- IP-based rate limiting

## Quick Start

```bash
pip install ncorn
ncorn module:app
```

## Requirements

- Python 3.11+
- httptools
- rich

## Links

- [GitHub](https://github.com/ndugram/ncorn)
- [Documentation](https://ncorn.readthedocs.io/)
