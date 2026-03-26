# WebSockets

WebSockets provide full-duplex communication between client and server.

## Status

!!! warning "Coming Soon"
    WebSocket support is planned for a future release.

Currently, ncorn supports HTTP/1.1 only. WebSocket support will be added in a future version.

## What are WebSockets?

WebSockets differ from HTTP:

- **HTTP**: Request-response model
- **WebSocket**: Bidirectional, persistent connection

## ASGI WebSocket Scope

```python
{
    "type": "websocket",
    "path": "/ws",
    "query_string": b"",
    "headers": [...],
    "client": ("127.0.0.1", 8000),
    "server": ("127.0.0.1", 8000),
    "subprotocols": [],
    "asgi": {"version": "3.0"},
}
```

## WebSocket Messages

### Connect

```python
{"type": "websocket.connect"}
```

### Receive

```python
{"type": "websocket.receive", "text": "hello"}
# or
{"type": "websocket.receive", "bytes": b"hello"}
```

### Send

```python
{"type": "websocket.send", "text": "hello"}
# or
{"type": "websocket.send", "bytes": b"hello"}
```

### Disconnect

```python
{"type": "websocket.disconnect", "code": 1000}
```

## Alternative

For now, you can use uvicorn alongside ncorn for WebSocket support, or use a reverse proxy that handles WebSocket upgrading.
