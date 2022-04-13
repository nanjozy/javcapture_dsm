# -*- coding: utf-8 -*-
from pathlib import Path


def get_flask_config(session_enabled: bool = True, session_expired: int = 60 * 60 * 24,
                     uwsgi_cache_enabled: bool = False):
    from ..setting import Row
    from ..func import suid
    return {
        "FLASK": {
            "secret_key": Row(default=suid(), cfg_type=str),
            "session_enabled": Row(default=session_enabled, cfg_type=bool),
            "session_expired": Row(default=session_expired, cfg_type=int),
            "session_type": Row(default="filesystem", cfg_type=str),
            "cookie_prefix": Row(default=suid(), cfg_type=str),
            "uwsgi_cache_enabled": Row(default=uwsgi_cache_enabled, cfg_type=bool),
        }
    }


def flask_config() -> dict:
    from ..setting import config
    cfg = config("FLASK")
    if cfg is None:
        cfg = {}
    return cfg


def cookie_prefix() -> str:
    return flask_config().get("cookie_prefix")


def session_enabled() -> bool:
    return flask_config().get("session_enabled")


def session_type() -> str:
    t = flask_config().get("session_type")
    t = t.lower()
    if "mongo" in t:
        return "mongodb"
    return "filesystem"


def session_expired() -> int:
    return flask_config().get("session_expired")


def flask_secret_key() -> str:
    return flask_config().get("secret_key")


def public_path():
    from ..setting import root
    return Path(root(), "public").absolute().as_posix()


def session_path():
    from ..func import get_tmp_path
    return get_tmp_path("session").as_posix()


def send_static(file: str):
    from flask import current_app
    return current_app.send_static_file(file)


def uwsgi_cache_enabled():
    return flask_config().get("uwsgi_cache_enabled")
