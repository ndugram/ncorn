# Quick Start

## Installation

```bash
pip install ncorn
```

## Basic Usage

Create a FastAPI application:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from ncorn!"}
```

Run with ncorn:

```bash
ncorn module:app
```

## Command Line Options

```bash
ncorn module:app --host 0.0.0.0 --port 8080
```

## Options

- `--host` - Host to bind to (default: 127.0.0.1)
- `--port` - Port to bind to (default: 8000)
- `--reload` - Enable auto-reload on file changes
- `--workers` - Number of worker processes (default: 1)
