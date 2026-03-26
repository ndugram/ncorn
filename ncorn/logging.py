import sys
import datetime
from typing import Any, Annotated
from dataclasses import dataclass

from annotated_doc import Doc


def get_timestamp() -> Annotated[
    str,
    Doc("Current timestamp in HH:MM:SS.mmm format")
]:
    """Get current timestamp."""
    return datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]


class Colors:
    """ANSI color codes."""
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GREY = "\033[90m"
    BOLD = "\033[1m"
    DIM = "\033[2m"


@dataclass
class RequestLog:
    """Request log entry."""
    method: Annotated[
        str,
        Doc("HTTP method")
    ]
    path: Annotated[
        str,
        Doc("Request path")
    ]
    status: Annotated[
        int,
        Doc("HTTP status code")
    ]
    latency: Annotated[
        float,
        Doc("Request processing time in seconds")
    ]
    client_ip: Annotated[
        str,
        Doc("Client IP address")
    ]


class Logger:
    """Logger with uvicorn-style output."""

    def __init__(self, verbose: Annotated[
        bool,
        Doc("Enable debug logging")
    ] = False, use_colors: Annotated[
        bool,
        Doc("Enable colored output")
    ] = True):
        self.verbose = verbose
        self.use_colors = use_colors
        self._is_tty = sys.stdout.isatty()

    def _colorize(self, text: Annotated[
        str,
        Doc("Text to colorize")
    ], color: Annotated[
        str,
        Doc("ANSI color code")
    ]) -> Annotated[
        str,
        Doc("Colorized text")
    ]:
        """Apply color to text."""
        if not self.use_colors or not self._is_tty:
            return text
        return f"{color}{text}{Colors.RESET}"

    def _format(self, level: Annotated[
        str,
        Doc("Log level")
    ], message: Annotated[
        str,
        Doc("Log message")
    ], color: Annotated[
        str,
        Doc("ANSI color code")
    ] = "") -> Annotated[
        str,
        Doc("Formatted log message")
    ]:
        """Format log message like uvicorn."""
        timestamp = self._colorize(get_timestamp(), Colors.GREY)
        level_str = self._colorize(level.ljust(8), color or Colors.WHITE)
        msg = self._colorize(message, color) if color else message
        return f"{timestamp} | {level_str} | {msg}"

    def info(self, message: Annotated[
        str,
        Doc("Info message")
    ], **kwargs: Any) -> None:
        """Log info message."""
        print(self._format("INFO", message, Colors.CYAN))

    def warning(self, message: Annotated[
        str,
        Doc("Warning message")
    ], **kwargs: Any) -> None:
        """Log warning message."""
        print(self._format("WARNING", message, Colors.YELLOW))

    def error(self, message: Annotated[
        str,
        Doc("Error message")
    ], **kwargs: Any) -> None:
        """Log error message."""
        print(self._format("ERROR", message, Colors.RED), file=sys.stderr)

    def success(self, message: Annotated[
        str,
        Doc("Success message")
    ], **kwargs: Any) -> None:
        """Log success message."""
        print(self._format("SUCCESS", message, Colors.GREEN))

    def server_start(self, host: Annotated[
        str,
        Doc("Server host")
    ], port: Annotated[
        int,
        Doc("Server port")
    ], workers: Annotated[
        int,
        Doc("Number of workers")
    ], protocol: Annotated[
        str,
        Doc("HTTP protocol (http or https)")
    ] = "http"
    ) -> None:
        """Log server startup."""
        addr = f"{protocol}://{host}:{port}"
        print()
        print(self._format("ncorn", "Application startup complete", Colors.CYAN))
        print(self._format("ncorn", f"Ncorn running on {addr} (Press CTRL+C to quit)", Colors.GREEN))
        print()

    def log_request(self, log: Annotated[
        RequestLog,
        Doc("Request log entry")
    ]) -> None:
        """Log HTTP request like uvicorn."""
        status = log.status
        if status < 400:
            status_color = Colors.GREEN
        elif status >= 500:
            status_color = Colors.RED
        else:
            status_color = Colors.YELLOW

        method = self._colorize(log.method.ljust(7), Colors.BLUE)
        path = log.path
        status_str = self._colorize(str(status), status_color)
        latency = self._colorize(f"{log.latency*1000:.0f}ms", Colors.GREY)

        print(f"{method} {path} {status_str} {latency}")

    def debug(self, message: Annotated[
        str,
        Doc("Debug message")
    ], **kwargs: Any) -> None:
        """Log debug message."""
        if self.verbose:
            print(self._format("DEBUG", message, Colors.GREY))


logger = Logger()
