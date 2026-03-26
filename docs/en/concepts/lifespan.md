# Lifespan

The lifespan protocol allows applications to perform startup and shutdown tasks.

## Overview

The lifespan protocol is part of ASGI and enables applications to:

- Initialize resources on startup
- Clean up resources on shutdown

## Usage with FastAPI

FastAPI handles lifespan automatically, but you can define custom handlers:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting up...")
    await connect_to_database()
    
    yield
    
    # Shutdown
    print("Shutting down...")
    await close_database()

app = FastAPI(lifespan=lifespan)
```

## Manual ASGI Implementation

If you're implementing ASGI directly:

```python
async def app(scope, receive, send):
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            
            if message["type"] == "lifespan.startup":
                # Initialize resources
                await send({"type": "lifespan.startup.complete"})
                
            elif message["type"] == "lifespan.shutdown":
                # Clean up resources
                await send({"type": "lifespan.shutdown.complete"})
                break
```

## ncorn Lifespan

ncorn fully supports the lifespan protocol:

- Calls startup events when server starts
- Calls shutdown events when server stops
- Handles graceful shutdown properly

## Startup Event

Triggered when the server is ready to accept connections:

```python
{"type": "lifespan.startup"}
```

Your app should respond with:

```python
{"type": "lifespan.startup.complete"}
# or
{"type": "lifespan.startup.failed", "message": "error reason"}
```

## Shutdown Event

Triggered when the server is shutting down:

```python
{"type": "lifespan.shutdown"}
```

Your app should respond with:

```python
{"type": "lifespan.shutdown.complete"}
# or
{"type": "lifespan.shutdown.failed", "message": "error reason"}
```
