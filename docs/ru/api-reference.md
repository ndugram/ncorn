# API Справочник

## Командная строка

### ncorn

```bash
ncorn module:app [ОПЦИИ]
```

Основная точка входа для запуска ncorn сервера.

### ncorn config

```bash
ncorn config
```

Создаёт файл конфигурации `ncorn.json` по умолчанию.

## Python API

### Config

```python
from ncorn.config import Config
```

Класс конфигурации для ncorn сервера.

```python
config = Config(
    host="127.0.0.1",
    port=8000,
    workers=1,
    reload=False,
    max_body_size=16 * 1024 * 1024,
    ssl_keyfile=None,
    ssl_certfile=None,
    ssl_version=5,
)
```

#### Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|------|--------------|----------|
| `host` | str | "127.0.0.1" | IP адрес для привязки |
| `port` | int | 8000 | Номер порта |
| `workers` | int | 1 | Количество воркеров |
| `reload` | bool | False | Включить авто-перезагрузку |
| `max_body_size` | int | 16777216 | Макс. размер тела запроса |
| `max_header_size` | int | 8192 | Макс. размер одного заголовка |
| `max_headers_total_size` | int | 65536 | Макс. общий размер заголовков |
| `header_timeout` | float | 30.0 | Таймаут чтения заголовков |
| `body_timeout` | float | 60.0 | Таймаут чтения тела |
| `request_timeout` | float | 10.0 | Таймаут обработки запроса |
| `keepalive_timeout` | float | 5.0 | Таймаут keep-alive |
| `keepalive_requests` | int | 100 | Макс. запросов на соединение |
| `max_headers` | int | 100 | Макс. количество заголовков |
| `max_connections` | int | 1000 | Макс. одновременных соединений |
| `max_connections_per_ip` | int | 50 | Макс. соединений с одного IP |
| `rate_limit_requests` | int | 100 | Запросов в окно |
| `rate_limit_window` | float | 60.0 | Окно rate limiting |
| `ssl_keyfile` | str | None | Путь к SSL ключу |
| `ssl_certfile` | str | None | Путь к SSL сертификату |
| `ssl_version` | int | 5 | Версия TLS (2-5) |

### HTTPServer

```python
from ncorn.server import HTTPServer
```

Класс HTTP сервера.

```python
server = HTTPServer(app, config)
await server.start()
await server.stop()
```

#### Методы

##### start(show_banner=True)

Запустить HTTP сервер.

##### stop()

Корректно остановить сервер.

### CLI функции

```python
from ncorn.cli import import_app, parse_args, main
```

#### import_app(app_spec: str)

Импортировать FastAPI приложение из строки "module:app".

#### parse_args(args: Optional[list[str]] = None) -> argparse.Namespace

Парсить аргументы командной строки.

#### main(args: Optional[list[str]] = None) -> None

Основная точка входа.

### Middleware

```python
from ncorn.middleware import (
    ValidationMiddleware,
    RateLimitMiddleware,
    MiddlewareChain,
)
```

#### ValidationMiddleware

Валидирует HTTP запросы (заголовки, размер тела).

#### RateLimitMiddleware

Реализует IP-based rate limiting.

#### MiddlewareChain

Объединяет несколько middleware вместе.

## Исключения

ncorn использует стандартные исключения Python. Смотрите документацию отдельных middleware для обработки ошибок.
