# ASGI

ASGI (Asynchronous Server Gateway Interface) is a standard interface between Python web servers and applications.

## Overview

ASGI is a specification that describes how async web applications should communicate with web servers. It was designed to replace WSGI (PEP 333) for async frameworks.

## Key Concepts

### Scope

The `scope` is a dictionary containing information about the connection:

```python
{
    "type": "http",
    "method": "GET",
    "path": "/",
    "query_string": b"",
    "headers": [(b"host", b"localhost")],
    "client": ("127.0.0.1", 8000),
    "server": ("127.0.0.1", 8000),
    "scheme": "http",
}
```

### Receive

The `receive` callable waits for incoming data:

```python
message = await receive()
# Returns: {"type": "http.request", "body": b"...", "more_body": bool}
```

### Send

The `send` callable sends response data:

```python
# Start response
await send({
    "type": "http.response.start",
    "status": 200,
    "headers": [(b"content-type", b"application/json")],
})

# Send body
await send({
    "type": "http.response.body",
    "body": b'{"message": "hello"}',
})
```

## HTTP Types

- `http` - Regular HTTP/1.1 connections
- `websocket` - WebSocket connections
- `lifespan` - Application lifecycle events

## ncorn ASGI Implementation

ncorn implements a full ASGI server:

- Parses HTTP/1.1 requests
- Builds ASGI scope dictionary
- Handles request/response lifecycle
- Supports keep-alive connections
- Implements HTTP/1.1 only (WebSocket coming soon)
