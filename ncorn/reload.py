import os
import sys
import time
import signal
import asyncio
import multiprocessing
from typing import Callable, Any, Annotated

from annotated_doc import Doc


class Reloader:
    """File system watcher for auto-reload."""

    def __init__(self, callback: Annotated[
        Callable[[], None],
        Doc("Callback function to call when files change")
    ], watch_dirs: Annotated[
        list[str] | None,
        Doc("List of directories to watch for changes")
    ] = None):
        self.callback = callback
        self.watch_dirs = watch_dirs or [os.getcwd()]
        self.mtimes: dict[str, float] = {}
        self.should_reload = False

    def start(self) -> None:
        """Start watching files."""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        while not self.should_reload:
            if self._check_files():
                self.callback()
            time.sleep(1)

    def stop(self) -> None:
        """Stop watching files."""
        self.should_reload = True

    def _signal_handler(self, signum: Annotated[
        int,
        Doc("Signal number")
    ], frame: Annotated[
        Any,
        Doc("Signal frame")
    ]) -> None:
        """Handle shutdown signals."""
        self.stop()

    def _check_files(self) -> Annotated[
        bool,
        Doc("True if any file changed")
    ]:
        """Check if any watched files changed."""
        for watch_dir in self.watch_dirs:
            if not os.path.isdir(watch_dir):
                continue
            for root, _, files in os.walk(watch_dir):
                if "__pycache__" in root or ".git" in root:
                    continue
                for file in files:
                    if not file.endswith(".py"):
                        continue
                    filepath = os.path.join(root, file)
                    try:
                        mtime = os.path.getmtime(filepath)
                        if filepath not in self.mtimes:
                            self.mtimes[filepath] = mtime
                        elif self.mtimes[filepath] != mtime:
                            self.mtimes[filepath] = mtime
                            return True
                    except OSError:
                        continue
        return False


def run_with_reload(
    app_path: Annotated[
        str,
        Doc("Application path in format 'module:app'")
    ],
    app_attr: Annotated[
        str,
        Doc("Application attribute name")
    ],
    host: Annotated[
        str,
        Doc("Server host")
    ],
    port: Annotated[
        int,
        Doc("Server port")
    ],
    config: Annotated[
        Any,
        Doc("Server configuration")
    ],
    middlewares: Annotated[
        list,
        Doc("List of middleware")
    ],
) -> None:
    """Run server with auto-reload."""
    worker_process = None

    def spawn_worker() -> None:
        nonlocal worker_process
        if worker_process and worker_process.is_alive():
            worker_process.terminate()
            worker_process.join()

        worker_process = multiprocessing.Process(
            target=_run_worker,
            args=(
                app_path,
                app_attr,
                host,
                port,
                config.max_body_size,
                config.header_timeout,
                config.rate_limit_requests,
                config.rate_limit_window,
            ),
        )
        worker_process.start()

    spawn_worker()
    reloader = Reloader(spawn_worker)

    try:
        reloader.start()
    finally:
        if worker_process and worker_process.is_alive():
            worker_process.terminate()
            worker_process.join()


def _run_worker(
    app_path: Annotated[
        str,
        Doc("Application path")
    ],
    app_attr: Annotated[
        str,
        Doc("Application attribute")
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
) -> None:
    """Run a single worker process."""
    from .server import HTTPServer
    from .config import Config

    app = _import_app(app_path, app_attr)
    config = Config(
        host=host,
        port=port,
        max_body_size=max_body_size,
        header_timeout=header_timeout,
        rate_limit_requests=rate_limit_requests,
        rate_limit_window=rate_limit_window,
    )
    server = HTTPServer(app, config)
    asyncio.run(server.start())


def _import_app(app_path: Annotated[
    str,
    Doc("Application path in format 'module:app'")
], app_attr: Annotated[
    str,
    Doc("Application attribute name")
]):
    """Import FastAPI app from path."""
    import importlib.util
    from types import ModuleType

    if ":" not in app_path:
        raise ValueError("App must be in format 'module:app'")

    module_path, attr_name = app_path.split(":", 1)

    current_dir = os.getcwd()
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    spec = importlib.util.find_spec(module_path)
    if spec is None:
        module = ModuleType(module_path)
        module.__file__ = module_path
        sys.modules[module_path] = module
    else:
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_path] = module
        spec.loader.exec_module(module)

    app = getattr(module, attr_name)
    return app


def create_worker_pool(
    app_path: Annotated[
        str,
        Doc("Application path")
    ],
    config: Annotated[
        Any,
        Doc("Server configuration")
    ],
    num_workers: Annotated[
        int,
        Doc("Number of workers")
    ],
) -> Annotated[
    list[multiprocessing.Process],
    Doc("List of worker processes")
]:
    """Create worker pool for multi-process mode."""
    workers = []
    for _ in range(num_workers):
        worker = multiprocessing.Process(
            target=_run_worker,
            args=(
                app_path,
                "app",
                config.host,
                config.port,
                config.max_body_size,
                config.header_timeout,
                config.rate_limit_requests,
                config.rate_limit_window,
            ),
        )
        worker.start()
        workers.append(worker)
    return workers
