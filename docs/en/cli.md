# CLI Reference

## Basic Command

```bash
ncorn module:app
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `app` | Application in format 'module:app' | Required |
| `--host` | Host to bind to | 127.0.0.1 |
| `--port` | Port to bind to | 8000 |
| `--reload` | Enable auto-reload on file changes | false |
| `--workers` | Number of worker processes | 1 |
| `--max-body-size` | Maximum request body size in bytes | 16777216 |
| `--header-timeout` | Header read timeout in seconds | 30.0 |
| `--rate-limit` | Rate limit requests per window | 100 |
| `--rate-limit-window` | Rate limit window in seconds | 60.0 |
| `--verbose` | Enable verbose logging | false |

## Examples

Run with custom host and port:

```bash
ncorn example_app:app --host 0.0.0.0 --port 9000
```

Run with auto-reload:

```bash
ncorn example_app:app --reload
```

Run with multiple workers:

```bash
ncorn example_app:app --workers 4
```

Run with custom rate limiting:

```bash
ncorn example_app:app --rate-limit 50 --rate-limit-window 30
```
