# coding:utf-8
import datetime
import getpass
import json
import sys
from copy import deepcopy
from logging import DEBUG, ERROR, INFO, info, WARNING, warning
from pathlib import Path
from platform import system
from typing import Callable

from .func import ensure_folder, merge_dict, set_no_proxy, set_proxy

__all__ = [
    "GlobalCfgCore",
    "ENTRY_NAME",
    "MACHINE_NAME",
    "NO_DISK",
    "no_log",
    "NO_LOG",
    "DEV_MODE",
    "ROOT",
    "RUNTIME",
    "LOG_PATH",
    "PLATFORM",
    "ENV",
    "Row",
    "Config",
    "config",
    "on_windows",
    "entry_name",
    "machine_name",
    "no_disk",
    "dev_mode",
    "root",
    "runtime",
    "log_path",
    "platform",
    "env",
]

ENTRY_NAME = None
MACHINE_NAME = None
NO_DISK = False
NO_LOG = False
DEV_MODE = True
ROOT = Path(".").as_posix()
RUNTIME = Path("runtime").as_posix()
LOG_PATH = Path("log").as_posix()
PLATFORM = system().lower()
ENV: str = "local"


# if PLATFORM != "windows":
#     assert getpass.getuser() != "root", "can not run on root user"


class Row:
    def __init__(self, default=None, cfg_type=None, msg: str = ""):
        self.default = default
        self.cfg_type = cfg_type
        self.msg = msg

    def get_default(self):
        return self.default


class Config:
    __DEFAULT = {
        "main": {
            "dev": Row(default=False, cfg_type=bool, msg="调试模式"),
            "proxy": Row(default="", cfg_type=str),
            "no_proxy": Row(
                default="127.0.0.1,localhost,local,.local",
                cfg_type=str),
            "RUNTIME": Row(default=None, cfg_type=str),
            "LOG": Row(default=None, cfg_type=str),
        },
    }

    @classmethod
    def DEFAULT(cls):
        return deepcopy(cls.__DEFAULT)

    def __init__(self, entry: str, root_path: str, env: str = None, configpath: str = None,
                 default: dict = None,
                 no_disk: bool = False, no_log: bool = False, logpath: str = None,
                 callback: Callable = None, log_level: int = INFO, help_info: str = None,
                 singleton: int = None, master: bool = False, ) -> None:
        self.master = master
        global ENTRY_NAME
        ENTRY_NAME = entry
        global ENV

        args = sys.argv[1:]
        for i, v in enumerate(args):
            if v in ["-h", "--help"]:
                if help_info is None:
                    help_info = """
                    -e\t--env\t[dev,uat,prd,...]
                    -l\t--log\t[info,debug,warning,error]
                    """
                info(help_info)
                exit(1)
            if v in ["-s", "--single"] and len(args) >= i + 1:
                singleton = int(args[i + 1])
                info("singleton port:", singleton)
            if v in ["-e", "--env"] and len(args) >= i + 1:
                env = args[i + 1]
            if v in ["-l", "--log"] and len(args) >= i + 1:
                t = args[i + 1]
                t = t.lower()
                mapping = {
                    "info": INFO,
                    "debug": DEBUG,
                    "warning": WARNING,
                    "error": ERROR,
                }
                t = mapping.get(t)
                if t is not None:
                    log_level = t
        if singleton is not None and ENTRY_NAME in ("__main__",):
            assert singleton >= 1024
            self.process_lock(singleton)
        if env:
            ENV = env.lower()
        self.no_disk = no_disk
        self.no_log = no_log
        global NO_DISK
        global NO_LOG
        NO_LOG = no_log
        NO_DISK = self.no_disk
        if root_path is None:
            p = Path(sys.argv[0]).absolute().parent
            root_path = p.as_posix()
        root_path = Path(root_path).absolute()
        if not root_path.is_dir():
            root_path = root_path.parent
        if logpath is not None:
            logp = Path(logpath).absolute()
        else:
            logp = Path(root_path, "data", "log").absolute()

        runtime_path = root_path.joinpath("data", "runtime")

        if ENV == "local":
            cfg_path = root_path.joinpath("data", "config.json")
        else:
            cfg_path = root_path.joinpath("data", "config.%s.json" % (ENV,))
        if configpath is not None:
            cfg_path = Path(configpath).absolute()

        global ROOT
        ROOT = root_path
        global RUNTIME
        RUNTIME = runtime_path
        global LOG_PATH
        LOG_PATH = logp
        global CFG_PATH
        CFG_PATH = cfg_path

        self.__path = cfg_path
        self.default_cfg = self.merge_vali(default)

        if cfg_path.exists():
            modet = "r"
            with open(cfg_path, modet, encoding="utf-8") as f:
                self.__conf = self.__merge_cfg(json.load(f), self.get_default())
        else:
            self.__conf = self.get_default()

        global DEV_MODE
        DEV_MODE = self.__conf["main"]["dev"]
        if self.__conf["main"]["LOG"] is not None:
            LOG_PATH = Path(self.__conf["main"]["LOG"]).absolute().as_posix()
        if self.__conf["main"]["RUNTIME"] is not None:
            RUNTIME = Path(self.__conf["main"]["RUNTIME"]).absolute().as_posix()

        if callable(callback):
            callback(self)

        self.write()

        if not self.no_disk:
            if not self.no_log:
                ensure_folder(LOG_PATH, mode=0o755)
            ensure_folder(RUNTIME, mode=0o755)
        global cfg
        cfg = self
        from .logging import set_level
        set_level(log_level)

        if self["main"]["proxy"]:
            _, proxy = set_proxy(self["main"]["proxy"])
        if self["main"]["no_proxy"]:
            no_proxy = set_no_proxy(self["main"]["no_proxy"])

        global MACHINE_NAME
        if MACHINE_NAME is None:
            name_path = Path(root(), "data", "machinename.txt").absolute()
            if name_path.exists():
                with open(name_path.as_posix(), "r", encoding="utf-8") as f:
                    MACHINE_NAME = f.read().strip()
            if not MACHINE_NAME:
                import socket
                MACHINE_NAME = socket.gethostname()
                if not no_disk:
                    with open(name_path.as_posix(), "w", encoding="utf-8") as f:
                        f.write(MACHINE_NAME)

        self.global_config_db: GlobalCfgCore = None

    def set_global_config_db(self, db):
        if "MONGO" in self.keys():
            self.global_config_db = db

    def init_global_configs(self):
        if self.global_config_db is not None:
            self.global_config_db.ensure_defaults()

    def get_default(self, obj: dict = None) -> dict:
        if obj is None:
            obj = deepcopy(self.default_cfg)
        for key, value in obj.items():
            if isinstance(value, dict):
                obj[key] = self.get_default(value)
            elif isinstance(value, Row):
                obj[key] = value.get_default()
        return obj

    def write(self):
        if not self.master:
            return
        if not self.no_disk:
            ensure_folder(Path(self.__path).parent.as_posix())
            with open(self.__path, mode="w+", encoding="utf-8", ) as f:
                json.dump(self.__conf, f, ensure_ascii=False, indent=4)

    def merge_vali(self, default: dict = None) -> dict:
        default_cfg = self.DEFAULT()
        if isinstance(default, dict):
            default_cfg = merge_dict(default_cfg, default)
        for k1, v1 in default.items():
            for k2, v2 in v1.items():
                if not isinstance(v2, Row):
                    default_cfg[k1][k2] = Row(default=v2)
        return default_cfg

    def __merge_cfg(self, obj: dict, default: dict) -> dict:
        for key, value in obj.items():
            if isinstance(value, Row):
                obj[key] = value.get_default()
        if isinstance(default, dict):
            for key1, value1 in default.items():
                if key1 not in obj.keys():
                    if isinstance(value1, Row):
                        value1 = value1.get_default()
                    obj[key1] = value1
        for key, value in obj.items():
            if isinstance(value, dict):
                obj[key] = self.__merge_cfg(value, default.get(key))
        return obj

    def __repr__(self):
        return repr(self.__conf)

    def keys(self):
        return self.__conf.keys()

    def values(self):
        return self.__conf.values()

    def items(self):
        return self.__conf.items()

    def __setitem__(self, key, value):
        self.__conf[key] = value

    def __getitem__(self, item: str):
        return self.__conf[item]

    def get(self, item: str):
        if item in self.__conf.keys():
            return self.__conf.get(item)
        if self.global_config_db is not None:
            return self.global_config_db.get_config_section(item)
        return {}

    def set(self, section, key, value):
        if isinstance(value, datetime.datetime):
            value = str(value)
        if section not in self.__conf:
            self.__conf[section] = {}
        self.__conf[section][key] = value
        with open(self.__path, mode="w", encoding="utf-8") as f:
            json.dump(self.__conf, f, ensure_ascii=False, indent=4)

    @classmethod
    def process_lock(cls, port: int):
        import socket
        try:
            singleton = socket.socket()
            host = socket.gethostname()
            singleton.bind((host, port))
            return
        except Exception as e:
            warning("singleton exit")
            exit(1)


class GlobalCfgCore:
    def ensure_defaults(self):
        pass

    def get_configs(self):
        pass

    def get_config_section(self, section: str):
        pass


cfg = None


def config(section: str = None) -> Config:
    global cfg
    assert isinstance(cfg, Config) is not None
    if section is None:
        return cfg
    res = cfg.get(section)
    return res


def on_windows():
    return PLATFORM == "windows"


def entry_name():
    global ENTRY_NAME
    return ENTRY_NAME


def env():
    global ENV
    return ENV


def machine_name():
    global MACHINE_NAME
    return MACHINE_NAME


def root():
    global ROOT
    return ROOT


def runtime():
    global RUNTIME
    return RUNTIME


def no_disk():
    global NO_DISK
    return NO_DISK


def no_log():
    global NO_LOG
    return NO_LOG


def dev_mode():
    global DEV_MODE
    return DEV_MODE


def log_path():
    global LOG_PATH
    return LOG_PATH


def platform():
    global PLATFORM
    return PLATFORM
