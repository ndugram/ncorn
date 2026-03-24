# Security

ncorn includes several security features to protect your application.

## Built-in Security Features

### Request Body Size Limit

Limits the maximum size of incoming request bodies to prevent DoS attacks.

```bash
ncorn app:app --max-body-size 8388608  # 8 MB
```

### Header Validation

Validates HTTP headers and rejects malformed requests.

### Timeout Protection

- `header_timeout` - Time limit for reading request headers
- `body_timeout` - Time limit for reading request body
- Prevents Slowloris attacks

```bash
ncorn app:app --header-timeout 30 --body-timeout 60
```

### IP Rate Limiting

Limits the number of requests from a single IP address.

```bash
ncorn app:app --rate-limit 100 --rate-limit-window 60
```

## Best Practices

1. Always set appropriate body size limits
2. Use rate limiting in production
3. Keep timeouts as low as possible for your use case
4. Run behind a reverse proxy like nginx for SSL/TLS termination
