# Server Behavior

## Lifecycle

ncorn follows the ASGI lifespan protocol to manage the application lifecycle.

### Startup

1. Load configuration from file, environment, or CLI arguments
2. Parse and validate application
3. Create SSL context if SSL is configured
4. Start ASGI server
5. Call lifespan `startup` event if defined

### Shutdown

1. Receive shutdown signal (SIGINT, SIGTERM)
2. Stop accepting new connections
3. Wait for active requests to complete (grace period)
4. Call lifespan `shutdown` event if defined
5. Close all connections
6. Exit process

## Connection Handling

### Keep-Alive

ncorn supports HTTP keep-alive connections to reuse TCP connections for multiple requests.

- Configurable via `--keepalive-timeout`
- Maximum requests per connection via `--keepalive-requests`

### Request Processing

1. Accept incoming TCP connection
2. Parse HTTP request headers
3. Validate headers (size, count, format)
4. Read request body if present
5. Call ASGI application
6. Send response
7. Keep connection alive or close

### Timeouts

ncorn implements multiple timeout layers:

- **header_timeout** - Time to receive all headers
- **body_timeout** - Time to read request body
- **keepalive_timeout** - Time to wait for next request on keep-alive connection
- **request_timeout** - Time for application to process request

## Multi-Worker Mode

When using `--workers > 1`, ncorn spawns multiple processes:

- Each worker runs its own event loop
- Workers share the same port (socket inheritance)
- Workers are restarted independently if they crash

## SSL/TLS

ncorn has native SSL/TLS support:

- TLS 1.3 (default), TLS 1.2, TLS 1.1, TLS 1.0
- Custom certificate and key files
- No reverse proxy required

## Logging

ncorn provides uvicorn-style logging:

```
21:50:53.290 | INFO     | SSL enabled: TLSv1.3
21:50:53.291 | ncorn    | Application startup complete
21:50:53.291 | ncorn    | Ncorn running on https://127.0.0.1:8443
```

Each request is logged with:
- HTTP method
- Path
- Status code
- Latency
