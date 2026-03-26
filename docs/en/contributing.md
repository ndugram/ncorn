# Contributing

Thank you for your interest in contributing to ncorn!

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/ndugram/ncorn.git
cd ncorn
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e .
pip install pytest httpx
```

## Code Style

- Follow PEP 8
- Use type hints
- Add docstrings using `annotated_doc`

## Testing

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=ncorn --cov-report=html
```

## Project Structure

```
ncorn/
├── __init__.py       # Package init
├── cli.py            # Command line interface
├── config.py         # Configuration class
├── config_file.py    # Config file loading
├── logging.py        # Logging utilities
├── main.py           # Main entry point
├── protocol.py       # HTTP protocol parser
├── reload.py         # Auto-reload functionality
├── server.py         # HTTP server
├── middleware/       # Middleware modules
│   ├── base.py
│   ├── ipfilter.py
│   ├── ratelimit.py
│   ├── security.py
│   ├── validation.py
│   └── waf.py
└── asgi.py          # ASGI adapter
```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## Reporting Issues

Please report bugs and feature requests via GitHub Issues.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
