import os
import sys
import asyncio
import argparse
import json
from typing import Optional

from .config import Config
from .config_file import load_config_from_file, create_default_config, get_config_path, CONFIG_FILE
from .server import HTTPServer
from .logging import logger
from .middleware import ValidationMiddleware, RateLimitMiddleware, MiddlewareChain
from .reload import run_with_reload


def parse_args(args: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog="ncorn",
        description="ASGI web server for FastAPI applications",
    )
    parser.add_argument(
        "app",
        nargs="?",
        default=None,
        help="Application in format 'module:app' or 'config' command",
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
        default=None,
        help="Enable auto-reload on file changes",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=None,
        help="Number of worker processes",
    )
    parser.add_argument(
        "--max-body-size",
        type=int,
        default=None,
        help="Maximum request body size in bytes",
    )
    parser.add_argument(
        "--header-timeout",
        type=float,
        default=None,
        help="Header read timeout in seconds",
    )
    parser.add_argument(
        "--body-timeout",
        type=float,
        default=None,
        help="Body read timeout in seconds",
    )
    parser.add_argument(
        "--keepalive-timeout",
        type=float,
        default=None,
        help="Keep-alive timeout in seconds",
    )
    parser.add_argument(
        "--max-headers",
        type=int,
        default=None,
        help="Maximum number of headers",
    )
    parser.add_argument(
        "--keepalive-requests",
        type=int,
        default=None,
        help="Max requests per keep-alive connection",
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
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    parser.add_argument(
        "--ssl-keyfile",
        default=None,
        help="Path to SSL key file",
    )
    parser.add_argument(
        "--ssl-certfile",
        default=None,
        help="Path to SSL certificate file",
    )
    parser.add_argument(
        "--ssl-version",
        type=int,
        default=None,
        choices=[2, 3, 4, 5],
        help="SSL/TLS version: 2=TLSv1, 3=TLSv1.1, 4=TLSv1.2, 5=TLSv1.3",
    )
    return parser.parse_args(args)


def merge_config(file_config: Config, args: argparse.Namespace) -> Config:
    """Merge file config with command line arguments."""
    return Config(
        host=args.host if args.host is not None else file_config.host,
        port=args.port if args.port is not None else file_config.port,
        workers=args.workers if args.workers is not None else file_config.workers,
        reload=args.reload if args.reload is not None else file_config.reload,
        max_body_size=args.max_body_size if args.max_body_size is not None else file_config.max_body_size,
        max_header_size=file_config.max_header_size,
        max_headers_total_size=file_config.max_headers_total_size,
        header_timeout=args.header_timeout if args.header_timeout is not None else file_config.header_timeout,
        body_timeout=args.body_timeout if args.body_timeout is not None else file_config.body_timeout,
        request_timeout=file_config.request_timeout,
        response_timeout=file_config.response_timeout,
        keepalive_timeout=args.keepalive_timeout if args.keepalive_timeout is not None else file_config.keepalive_timeout,
        keepalive_requests=args.keepalive_requests if args.keepalive_requests is not None else file_config.keepalive_requests,
        max_headers=args.max_headers if args.max_headers is not None else file_config.max_headers,
        max_connections=file_config.max_connections,
        max_connections_per_ip=file_config.max_connections_per_ip,
        rate_limit_requests=args.rate_limit if args.rate_limit is not None else file_config.rate_limit_requests,
        rate_limit_window=args.rate_limit_window if args.rate_limit_window is not None else file_config.rate_limit_window,
        write_buffer_limit=file_config.write_buffer_limit,
        drain_timeout=file_config.drain_timeout,
        ip_whitelist=file_config.ip_whitelist,
        ip_blacklist=file_config.ip_blacklist,
        enable_security_headers=file_config.enable_security_headers,
        waf_max_query_length=file_config.waf_max_query_length,
        ssl_keyfile=args.ssl_keyfile if args.ssl_keyfile is not None else file_config.ssl_keyfile,
        ssl_certfile=args.ssl_certfile if args.ssl_certfile is not None else file_config.ssl_certfile,
        ssl_version=args.ssl_version if args.ssl_version is not None else file_config.ssl_version,
    )


def validate_fastapi_app(app: any) -> None:
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


def import_app(app_spec: str):
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
    app: any,
    config: Config,
) -> None:
    """Run the server."""
    middlewares = [
        ValidationMiddleware(app, config),
        RateLimitMiddleware(app, config),
    ]

    chain = MiddlewareChain(app, middlewares)
    wrapped_app = chain.build()

    server = HTTPServer(wrapped_app, config, middlewares)

    try:
        await server.start()
    except KeyboardInterrupt:
        logger.info("Shutting down...")
        await server.stop()


def run_workers(app_spec: str, config: Config) -> None:
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
    app_spec: str,
    host: str,
    port: int,
    max_body_size: int,
    header_timeout: float,
    rate_limit_requests: int,
    rate_limit_window: float,
    worker_id: int,
) -> None:
    """Single worker process."""
    import time

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


def show_config() -> None:
    """Show current configuration."""
    config_path = get_config_path()
    
    if not config_path:
        create_default_config(CONFIG_FILE)
        logger.success(f"Created {CONFIG_FILE} with default configuration")


def main(args: Optional[list[str]] = None) -> None:
    """Main entry point."""
    parsed = parse_args(args)

    if parsed.app == "config":
        show_config()
        sys.exit(0)

    if not parsed.app:
        print("Usage: ncorn <app> [options]")
        print("       ncorn config")
        print("Run 'ncorn --help' for more information")
        sys.exit(1)

    file_config = load_config_from_file()
    config = merge_config(file_config, parsed)

    try:
        app = import_app(parsed.app)
    except Exception as e:
        logger.error(f"Failed to import app: {e}")
        sys.exit(1)

    if parsed.verbose:
        from .logging import logger as log
        log.verbose = True

    if parsed.reload:
        run_with_reload(
            parsed.app,
            "app",
            config.host,
            config.port,
            config,
            [],
        )
    elif config.workers > 1:
        protocol = "https" if (config.ssl_keyfile and config.ssl_certfile) else "http"
        logger.server_start(config.host, config.port, config.workers, protocol)
        run_workers(parsed.app, config)
    else:
        try:
            asyncio.run(run_server(app, config))
        except KeyboardInterrupt:
            logger.info("Server stopped")


if __name__ == "__main__":
    main()
