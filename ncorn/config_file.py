import json
from pathlib import Path
from typing import Optional

from .config import Config


CONFIG_FILE = "ncorn.json"


def get_config_path() -> Optional[str]:
    current_dir = Path(".")
    if (current_dir / CONFIG_FILE).exists():
        return str(current_dir / CONFIG_FILE)
    
    home_dir = Path.home()
    if (home_dir / CONFIG_FILE).exists():
        return str(home_dir / CONFIG_FILE)
    
    return None


def load_config_from_file(config_path: Optional[str] = None) -> Config:
    """Load configuration from ncorn.json file."""
    if config_path is None:
        config_path = get_config_path()
    
    if config_path is None or not Path(config_path).exists():
        return Config()
    
    with open(config_path, "r") as f:
        data = json.load(f)
    
    return Config(
        host=data.get("host", "127.0.0.1"),
        port=data.get("port", 8000),
        workers=data.get("workers", 1),
        reload=data.get("reload", False),
        max_body_size=data.get("max_body_size", 16 * 1024 * 1024),
        max_header_size=data.get("max_header_size", 8192),
        max_headers_total_size=data.get("max_headers_total_size", 65536),
        header_timeout=data.get("header_timeout", 30.0),
        body_timeout=data.get("body_timeout", 60.0),
        request_timeout=data.get("request_timeout", 10.0),
        response_timeout=data.get("response_timeout", 10.0),
        keepalive_timeout=data.get("keepalive_timeout", 5.0),
        keepalive_requests=data.get("keepalive_requests", 100),
        max_headers=data.get("max_headers", 100),
        max_connections=data.get("max_connections", 1000),
        max_connections_per_ip=data.get("max_connections_per_ip", 50),
        rate_limit_requests=data.get("rate_limit_requests", 100),
        rate_limit_window=data.get("rate_limit_window", 60.0),
        write_buffer_limit=data.get("write_buffer_limit", 65536),
        drain_timeout=data.get("drain_timeout", 1.0),
        ip_whitelist=data.get("ip_whitelist", []),
        ip_blacklist=data.get("ip_blacklist", []),
        enable_security_headers=data.get("enable_security_headers", True),
        waf_max_query_length=data.get("waf_max_query_length", 4096),
        ssl_keyfile=data.get("ssl_keyfile"),
        ssl_certfile=data.get("ssl_certfile"),
        ssl_version=data.get("ssl_version", 5),
    )


def create_default_config(path: Optional[str] = None) -> None:
    """Create default ncorn.json config file."""
    if path is None:
        path = CONFIG_FILE
    
    config = Config()
    config_dict = {
        "host": config.host,
        "port": config.port,
        "workers": config.workers,
        "reload": config.reload,
        "max_body_size": config.max_body_size,
        "max_header_size": config.max_header_size,
        "max_headers_total_size": config.max_headers_total_size,
        "header_timeout": config.header_timeout,
        "body_timeout": config.body_timeout,
        "request_timeout": config.request_timeout,
        "response_timeout": config.response_timeout,
        "keepalive_timeout": config.keepalive_timeout,
        "keepalive_requests": config.keepalive_requests,
        "max_headers": config.max_headers,
        "max_connections": config.max_connections,
        "max_connections_per_ip": config.max_connections_per_ip,
        "rate_limit_requests": config.rate_limit_requests,
        "rate_limit_window": config.rate_limit_window,
        "write_buffer_limit": config.write_buffer_limit,
        "drain_timeout": config.drain_timeout,
        "ip_whitelist": config.ip_whitelist,
        "ip_blacklist": config.ip_blacklist,
        "enable_security_headers": config.enable_security_headers,
        "waf_max_query_length": config.waf_max_query_length,
        "ssl_keyfile": config.ssl_keyfile,
        "ssl_certfile": config.ssl_certfile,
        "ssl_version": config.ssl_version,
    }
    
    with open(path, "w") as f:
        json.dump(config_dict, f, indent=2)
