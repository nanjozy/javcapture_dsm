# -*- coding: utf-8 -*-
from abc import ABC
from logging import DEBUG, ERROR, FATAL, INFO, NOTSET, WARNING
from multiprocessing import freeze_support, Process
from pathlib import Path

from .func import merge_dict
from .setting import Config, on_windows, Row

__all__ = [
    "Entry",
    "Row",
    "WebEntry",
    "GcLogEntry",
]

instance = None


class Entry(ABC):
    LOCAL = "local"
    DEV = "dev"
    SIT = "sit"
    UAT = "uat"
    PRD = "prd"
    NOTSET = NOTSET
    INFO = INFO
    WARNING = WARNING
    DEBUG = DEBUG
    ERROR = ERROR
    FATAL = FATAL
    TRACE = 35
    TRACK = 1
    DEVELOP = 5

    def __init__(self, name: str, log_name: str, file: str, env: str = PRD,
                 log_level: int = INFO, cfg_master: bool = False, log_recycle: bool = False,
                 no_disk: bool = False, no_log: bool = False, singleton: int = None):
        self.name = name
        self.log_name = log_name
        self.file = file
        self.env = env
        self.cfg_master = cfg_master
        self.log_level = log_level
        self.log_recycle = log_recycle
        self.no_disk = no_disk
        self.app = None
        self.onced = False
        self.no_log = no_log
        DEFAULT = Config.DEFAULT()

        default = merge_dict(DEFAULT, self.default_config(), deep_copy=True)
        self.default = default
        self.singleton = singleton

        self.re_init()

        self.log.track("Entry: %s", self.name)
        from .func import in_uwsgi
        if self.name == '__main__':
            self._once()
        elif in_uwsgi() and self.name in ("main", "web", "entry_web") and self.log_name == "web":
            self._once()
            self.uwsgi_main()
        if self.name == '__main__':
            self.main()
        # if isinstance(self.gc_log_process, Process):
        #     if self.gc_log_process.is_alive():
        #         self.gc_log_process.terminate()

    def re_init(self):
        self.config = Config(self.name, root_path=self.file, env=self.env, default=self.default_config(),
                             log_level=self.log_level,
                             no_disk=self.no_disk, no_log=self.no_log, singleton=self.singleton, master=self.cfg_master)
        from .logging import init_logger, Logger
        self.log: Logger = init_logger(name=self.log_name)
        gcdb = self.get_global_config_db()
        self.config.set_global_config_db(gcdb)
        from .func import in_uwsgi
        if (self.name == '__main__') or (in_uwsgi() and self.name in ("main", "web") and self.log_name == "web"):
            self.config.init_global_configs()
        self.app = self.init()
        from .setting import root
        self.log.track("Enter Name:\t%s\nROOT:\t%s", self.name, root())
        global instance
        instance = self

    @classmethod
    def file_path(cls, path: str, parent: int = 0):
        path = Path(path).resolve()
        if path.is_dir():
            pass
        else:
            path = path.parent
        for i in range(parent):
            path = path.parent
        return path.as_posix()

    def _once(self):
        if self.onced:
            return
        self.onced = True
        if self.log_recycle:
            from .logging import gc_log
            if on_windows():
                freeze_support()
            p = Process(target=gc_log, daemon=True)
            p.start()
        self.once()

    def once(self):
        pass

    def flask_app(self):
        from flask import Flask
        app: Flask = self.app
        return app

    def default_config(self) -> dict:
        example = {
            "example": {
                "example": Row(default="example", cfg_type=str, msg="Example"),
            },
        }
        return {}

    def global_default_configs(self) -> dict:
        example = {
            "example": {
                "example": Row(default="example", cfg_type=str, msg="Example"),
            },
        }
        return None

    def get_global_config_db(self):
        defaults = self.global_default_configs()
        if defaults is not None and "MONGO" in self.default_config().keys():
            from .mongo import GlobalCFG
            GlobalCFG.set_default_configs(defaults)
            db = GlobalCFG()
            return db
        return None

    def init(self):
        pass

    def main(self):
        pass

    def uwsgi_main(self):
        pass


class WebEntry(Entry):
    def __init__(self, name: str, log_name: str, file: str, env: str = Entry.PRD,
                 log_level: int = Entry.INFO, cfg_master: bool = False, log_recycle: bool = False, port: int = 5000,
                 no_disk: bool = False, no_log: bool = False):
        self.port = port
        super().__init__(name, log_name, file, env=env, log_level=log_level, cfg_master=cfg_master,
                         log_recycle=log_recycle, no_disk=no_disk, no_log=no_log, )

    def init(self):
        from .flask import init_app
        app = init_app()
        app = self.web_init(app)
        return app

    def web_init(self, app):
        return app

    def main(self):
        self.flask_app().run(host="0.0.0.0", port=self.port, debug=False, load_dotenv=False)


class GcLogEntry(Entry):
    def __init__(self, name: str, file: str, env: str = Entry.PRD,
                 log_level: int = Entry.INFO, ):
        super().__init__(name, "gc_log", file, env=env, log_level=log_level, cfg_master=False,
                         log_recycle=True, no_disk=False)

    def once(self):
        if self.onced:
            return
        self.onced = True
        # if self.log_recycle:
        #     from .logging import gc_log
        #     gc_log()


def get_instance() -> Entry:
    global instance
    return instance
