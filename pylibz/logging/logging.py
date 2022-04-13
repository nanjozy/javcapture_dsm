# -*- coding: utf-8 -*-
from logging import basicConfig, captureWarnings, DEBUG, ERROR, INFO, Logger as LoggerCore, WARNING
from typing import ClassVar

from .func import get_file_handler, getLogger, LOGGING_FORMAT_STR
from .logger import Logger


class log:
    INFO = INFO
    DEBUG = DEBUG
    WARNING = WARNING
    ERROR = ERROR

    cls = Logger

    def __new__(cls, name: str = None):
        global log_instance, log_name
        if name is None:
            name = log_name
        if not has_log(name, cls.cls):
            log_instance[name] = getLogger(name, cls=cls.cls)
        res: Logger = log_instance.get(name)
        return res


def set_level(level: int):
    global log_level
    log_level = level
    return log_level


def set_log_name(name: str):
    global log_name
    log_name = name
    return log_name


def set_log_cls(cls: ClassVar):
    assert issubclass(cls, Logger)
    log.cls = cls


def has_log(name: str, cls: ClassVar = None) -> bool:
    if cls is None:
        cls = log.cls
    return isinstance(log_instance.get(name), cls)


def init_logger(name: str = None, err_seperate=True, cls: ClassVar = None, when: str = "D",
                backup: int = 90) -> LoggerCore:
    global log_when, log_backup, log_instance, log_name
    captureWarnings(True)
    log_when = when.upper().strip()
    log_backup = backup
    if name is None:
        name = log_name
    else:
        log_name = name
    file_handler = get_file_handler(name + ".basic", ERROR)
    if file_handler:
        basicConfig(
            format=LOGGING_FORMAT_STR,
            level=INFO,
            handlers=[file_handler],
        )
    else:
        basicConfig(
            format=LOGGING_FORMAT_STR,
            level=INFO,
        )
    log_instance[name] = getLogger(name=name, level=None, err_seperate=err_seperate, cls=cls)
    return log_instance.get(name)


log_instance = {}
log_name = "pylibz"
log_level = INFO
log_when = "D"
log_backup = 90
