# -*- coding: utf-8 -*-

from pylibz.entry import WebEntry


class Main(WebEntry):
    def default_config(self) -> dict:
        from .config import default_config
        return default_config()

    def web_init(self, app):
        from .api import bind_router
        bind_router(app)
        return app
