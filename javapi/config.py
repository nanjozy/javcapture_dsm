# -*- coding: utf-8 -*-
def default_config() -> dict:
    from pylibz.setting import Row
    from pylibz.flask import get_flask_config
    DEFAULT = {
        "main": {
            "dev": Row(default=False, cfg_type=bool, msg="调试模式"),
            "proxy": Row(default="", cfg_type=str),
            "no_proxy": Row(default="127.0.0.1,localhost,local,.local",
                            cfg_type=str),
            "RUNTIME": Row(default=None, cfg_type=str),
            "LOG": Row(default=None, cfg_type=str),
        },
        "javdb": {
            "local": Row(default="http://172.17.0.1:5004", cfg_type=str),
            "host": Row(default="https://javdb39.com", cfg_type=str),
        }
    }
    DEFAULT.update(get_flask_config(session_enabled=False, uwsgi_cache_enabled=False))
    return DEFAULT


def get_javdb_host():
    from pylibz import config
    host = config("javdb").get("host")
    return host.strip().strip("/")
def get_local():
    from pylibz import config
    host = config("javdb").get("local")
    return host.strip().strip("/")
