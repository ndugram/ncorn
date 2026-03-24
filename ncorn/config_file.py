import configparser
from pathlib import Path

from .config import Config


def load_config_from_file(config_path: str | None = None) -> Config:
    """Load configuration from ncorn.cnf file."""
    if config_path is None:
        config_path = "ncorn.cnf"

    config_file = Path(config_path)

    if not config_file.exists():
        return Config()

    parser = configparser.ConfigParser()
    parser.read(config_file)

    if "ncorn" not in parser:
        return Config()

    section = parser["ncorn"]

    return Config(
        host=section.get("host", "127.0.0.1"),
        port=section.getint("port", 8000),
        workers=section.getint("workers", 1),
        reload=section.getboolean("reload", False),
        max_body_size=section.getint("max_body_size", 16 * 1024 * 1024),
        header_timeout=section.getfloat("header_timeout", 30.0),
        body_timeout=section.getfloat("body_timeout", 60.0),
        keepalive_timeout=section.getfloat("keepalive_timeout", 5.0),
        max_headers=section.getint("max_headers", 100),
        max_keepalive_requests=section.getint("max_keepalive_requests", 100),
        rate_limit_requests=section.getint("rate_limit_requests", 100),
        rate_limit_window=section.getfloat("rate_limit_window", 60.0),
    )


def find_config_file() -> str | None:
    """Find ncorn.cnf in current directory or home directory."""
    current_dir = Path(".")
    if (current_dir / "ncorn.cnf").exists():
        return "ncorn.cnf"

    home_dir = Path.home()
    if (home_dir / "ncorn.cnf").exists():
        return str(home_dir / "ncorn.cnf")

    return None
