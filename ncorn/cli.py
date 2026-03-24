import os
import sys
import asyncio
import argparse
from typing import Optional, Annotated

from annotated_doc import Doc

from .config import Config
from .server import HTTPServer
from .logging import logger
from .middleware import ValidationMiddleware, RateLimitMiddleware, MiddlewareChain, IPFilterMiddleware, SecurityHeadersMiddleware, WAFMiddleware
from .reload import run_with_reload


def parse_args(args: Annotated[
    Optional[list[str]],
    Doc("Command line arguments")
]) -> Annotated[
    argparse.Namespace,
    Doc("Parsed arguments")
]:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="ncorn",
        description="ASGI web server for FastAPI applications",
    )
    parser.add_argument(
        "app",
        nargs="?",
        default=None,
        help="Application in format 'module:app'",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default=None,
        choices=["run", "config"],
        help="Command (run or config)",
    )
    parser.add_argument(
        "--host",
        default=None,
        help="Host to bind to",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="Port to bind to",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of workers",
    )
    parser.add_argument(
        "--max-body-size",
        type=int,
        default=None,
        help="Max body size in bytes",
    )
    parser.add_argument(
        "--max-header-size",
        type=int,
        default=None,
        help="Max size of a single header",
    )
    parser.add_argument(
        "--max-headers-total-size",
        type=int,
        default=None,
        help="Max total size of all headers",
    )
    parser.add_argument(
        "--header-timeout",
        type=float,
        default=None,
        help="Header read timeout",
    )
    parser.add_argument(
        "--body-timeout",
        type=float,
        default=None,
        help="Body read timeout",
    )
    parser.add_argument(
        "--request-timeout",
        type=float,
        default=None,
        help="Request processing timeout",
    )
    parser.add_argument(
        "--max-connections",
        type=int,
        default=None,
        help="Max total connections",
    )
    parser.add_argument(
        "--max-connections-per-ip",
        type=int,
        default=None,
        help="Max connections per IP",
    )
    parser.add_argument(
        "--keepalive-requests",
        type=int,
        default=None,
        help="Max requests per keep-alive connection",
    )
    parser.add_argument(
        "--keepalive-timeout",
        type=float,
        default=None,
        help="Keep-alive timeout",
    )
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=None,
        help="Rate limit requests per window",
    )
    parser.add_argument(
        "--rate-limit-window",
        type=float,
        default=None,
        help="Rate limit window in seconds",
    )
    parser.add_argument(
        "--ip-blacklist",
        nargs="*",
        default=None,
        help="IP addresses to block",
    )
    parser.add_argument(
        "--ip-whitelist",
        nargs="*",
        default=None,
        help="IP addresses to allow (blocks all others)",
    )
    parser.add_argument(
        "--no-security-headers",
        action="store_true",
        help="Disable security headers",
    )
    parser.add_argument(
        "--waf-max-query-length",
        type=int,
        default=None,
        help="Max query string length for WAF",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose logging",
    )
    return parser.parse_args(args)


def validate_fastapi_app(app: Annotated[
    any,
    Doc("FastAPI application to validate")
]) -> Annotated[
    None,
    Doc("Raises ValueError if not a FastAPI app")
]:
    """Validate that the app is a FastAPI application."""
    if app is None:
        raise ValueError("Application is None")

    if not hasattr(app, "routes"):
        raise ValueError(
            "Application does not appear to be a FastAPI app. "
            "ncorn only supports FastAPI applications."
        )

    if not hasattr(app, "asgi_app") and not hasattr(app, "router"):
        raise ValueError(
            "Application does not appear to be a FastAPI app. "
            "ncorn only supports FastAPI applications."
        )


def import_app(app_spec: Annotated[
    str,
    Doc("Application in format 'module:app'")
]) -> Annotated[
    any,
    Doc("FastAPI application instance")
]:
    """Import application from module:app string."""
    if ":" not in app_spec:
        raise ValueError("App must be in format 'module:app'")

    module_path, attr_name = app_spec.split(":", 1)

    import importlib.util
    from types import ModuleType

    current_dir = os.getcwd()
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    spec = importlib.util.find_spec(module_path)
    if spec is None:
        module = ModuleType(module_path)
        module.__file__ = module_path
        sys.modules[module_path] = module
        raise ImportError(f"Cannot find module '{module_path}'")
    else:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_path] = module
        spec.loader.exec_module(module)

    if not hasattr(module, attr_name):
        raise AttributeError(f"Module '{module_path}' has no attribute '{attr_name}'")

    app = getattr(module, attr_name)
    validate_fastapi_app(app)
    return app


async def run_server(
    app: Annotated[
        any,
        Doc("FastAPI application")
    ],
    config: Annotated[
        Config,
        Doc("Server configuration")
    ],
) -> Annotated[
    None,
    Doc("Runs server until interrupted")
]:
    """Run the server."""
    middlewares = [
        IPFilterMiddleware(app, config),
        WAFMiddleware(app, config),
        ValidationMiddleware(app, config),
        RateLimitMiddleware(app, config),
        SecurityHeadersMiddleware(app, config),
    ]

    chain = MiddlewareChain(app, middlewares)
    wrapped_app = chain.build()

    server = HTTPServer(wrapped_app, config, middlewares)

    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await server.stop()


def run_workers(app_spec: Annotated[
    str,
    Doc("Application in format 'module:app'")
], config: Annotated[
    Config,
    Doc("Server configuration")
]) -> Annotated[
    None,
    Doc("Runs multiple worker processes")
]:
    """Run multiple worker processes."""
    import multiprocessing

    workers = []
    for i in range(config.workers):
        worker = multiprocessing.Process(
            target=_worker_process,
            args=(
                app_spec,
                config.host,
                config.port,
                config.max_body_size,
                config.header_timeout,
                config.rate_limit_requests,
                config.rate_limit_window,
                i,
            ),
        )
        worker.start()
        workers.append(worker)

    try:
        for worker in workers:
            worker.join()
    except KeyboardInterrupt:
        logger.info("Shutting down workers...")
        for worker in workers:
            if worker.is_alive():
                worker.terminate()
                worker.join()


def _worker_process(
    app_spec: Annotated[
        str,
        Doc("Application in format 'module:app'")
    ],
    host: Annotated[
        str,
        Doc("Server host")
    ],
    port: Annotated[
        int,
        Doc("Server port")
    ],
    max_body_size: Annotated[
        int,
        Doc("Max body size")
    ],
    header_timeout: Annotated[
        float,
        Doc("Header timeout")
    ],
    rate_limit_requests: Annotated[
        int,
        Doc("Rate limit requests")
    ],
    rate_limit_window: Annotated[
        float,
        Doc("Rate limit window")
    ],
    worker_id: Annotated[
        int,
        Doc("Worker ID for staggered startup")
    ],
) -> Annotated[
    None,
    Doc("Single worker process")
]:
    """Single worker process."""
    import time
    from .config import Config

    time.sleep(worker_id * 0.1)

    try:
        app = import_app(app_spec)
        config = Config(
            host=host,
            port=port,
            workers=1,
            max_body_size=max_body_size,
            header_timeout=header_timeout,
            rate_limit_requests=rate_limit_requests,
            rate_limit_window=rate_limit_window,
        )

        middlewares = [
            ValidationMiddleware(app, config),
            RateLimitMiddleware(app, config),
        ]

        chain = MiddlewareChain(app, middlewares)
        wrapped_app = chain.build()

        server = HTTPServer(wrapped_app, config, middlewares)
        asyncio.run(server.start(show_banner=False))
    except KeyboardInterrupt:
        pass
    except Exception:
        pass


def main(args: Annotated[
    Optional[list[str]],
    Doc("Command line arguments")
] = None) -> Annotated[
    None,
    Doc("Main entry point")
]:
    """Main entry point."""
    parsed = parse_args(args)

    app_arg = parsed.app

    if not app_arg:
        print("Usage: ncorn <app> [options]")
        print("Run 'ncorn --help' for more information")
        sys.exit(1)

    ip_whitelist = parsed.ip_whitelist if parsed.ip_whitelist else []
    ip_blacklist = parsed.ip_blacklist if parsed.ip_blacklist else []

    config = Config(
        host=parsed.host if parsed.host else "127.0.0.1",
        port=parsed.port if parsed.port else 8000,
        workers=parsed.workers if parsed.workers else 1,
        reload=parsed.reload if parsed.reload else False,
        max_body_size=parsed.max_body_size if parsed.max_body_size else 16 * 1024 * 1024,
        max_header_size=parsed.max_header_size if parsed.max_header_size else 8192,
        max_headers_total_size=parsed.max_headers_total_size if parsed.max_headers_total_size else 65536,
        header_timeout=parsed.header_timeout if parsed.header_timeout else 30.0,
        body_timeout=parsed.body_timeout if parsed.body_timeout else 60.0,
        request_timeout=parsed.request_timeout if parsed.request_timeout else 10.0,
        keepalive_requests=parsed.keepalive_requests if parsed.keepalive_requests else 100,
        keepalive_timeout=parsed.keepalive_timeout if parsed.keepalive_timeout else 5.0,
        max_connections=parsed.max_connections if parsed.max_connections else 1000,
        max_connections_per_ip=parsed.max_connections_per_ip if parsed.max_connections_per_ip else 50,
        rate_limit_requests=parsed.rate_limit if parsed.rate_limit else 100,
        rate_limit_window=parsed.rate_limit_window if parsed.rate_limit_window else 60.0,
        ip_whitelist=ip_whitelist,
        ip_blacklist=ip_blacklist,
        enable_security_headers=not parsed.no_security_headers if hasattr(parsed, 'no_security_headers') else True,
        waf_max_query_length=parsed.waf_max_query_length if parsed.waf_max_query_length else 4096,
    )

    try:
        app = import_app(app_arg)
    except Exception as e:
        logger.error(f"Failed to import app: {e}")
        sys.exit(1)

    if parsed.verbose:
        from .logging import logger as log
        log.verbose = True

    if config.reload:
        run_with_reload(
            app_arg,
            "app",
            config.host,
            config.port,
            config,
            [],
        )
    elif config.workers > 1:
        logger.server_start(config.host, config.port, config.workers)
        run_workers(app_arg, config)
    else:
        try:
            asyncio.run(run_server(app, config))
        except KeyboardInterrupt:
            logger.info("Server stopped")


if __name__ == "__main__":
    main()