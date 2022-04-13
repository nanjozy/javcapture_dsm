# -*- coding: utf-8 -*-
import logging.handlers
import traceback as __traceback
from pathlib import Path
from typing import ClassVar

from .file_handler import FileHandler
from .multiprocess_handler import MultiprocessHandler
from .std_handler import StdHandler
from ..func import ensure_folder

LOGGING_FORMAT_STR = "##%s##\n%s\n**%s**\n" % (
    '[%(asctime)s %(levelname)s %(name)s PID:%(process)d %(threadName)s]',
    "%(message)s",
    "[\"%(pathname)s:%(lineno)s\" func: %(funcName)s]")
logging_format = logging.Formatter(LOGGING_FORMAT_STR)

ERR_PREFIX = "exception."


def getLogPath(prefix="log", dirOnly=False):
    from ..setting import log_path
    if dirOnly:
        return log_path()
    return Path(log_path(), str(prefix) + ".txt").absolute().as_posix()


def getLogPathDate(prefix="log", dirOnly=False):
    from ..setting import log_path
    if dirOnly:
        return log_path()
    return Path(log_path(), str(prefix) + ".{date}.{num}.txt").absolute().as_posix()


def get_file_handler(name: str, level: int = logging.INFO):
    global logging_format
    from ..setting import no_disk, no_log
    if not no_disk() and not no_log():
        from .logging import log_when, log_backup
        ensure_folder(getLogPath(name, dirOnly=True), mode=0o666)
        when = log_when
        assert when in ["D", "H", "M", "S"]
        backupCount = log_backup
        if when == "D":
            backupCount = backupCount * 1
        elif when == "H":
            backupCount = backupCount * 24
        elif when == "M":
            backupCount = backupCount * 24 * 60
        elif when == "S":
            backupCount = backupCount * 24 * 60 * 60
        file_handler = FileHandler(getLogPath(name), encoding='utf-8', delay=True)
        # file_handler = MultiprocessHandler(getLogPath(name), when=when, backupCount=backupCount,
        #                                    encoding='utf-8', )
        file_handler.setFormatter(logging_format)
        file_handler.setLevel(level)
    else:
        file_handler = None
    return file_handler


def addHandler(logger: logging.Logger, name: str = __name__, level: int = logging.INFO, log2file: bool = True,
               err_seperate: bool = True):
    global logging_format
    has_stream = False
    has_file = False
    for h in logger.handlers:
        if isinstance(h, StdHandler):
            has_stream = True
        elif isinstance(h, (FileHandler, MultiprocessHandler)):
            has_file = True
        if has_stream and has_file:
            break
    if not has_stream:
        stream_handler = StdHandler()
        stream_handler.setLevel(level)
        stream_handler.setFormatter(logging_format)
        logger.addHandler(stream_handler)
    if log2file and not has_file:
        file_handler = get_file_handler(name, level)
        if file_handler is not None:
            logger.addHandler(file_handler)
        # if err_seperate:
        #     file_handler = get_file_handler(ERR_PREFIX + name, logging.WARNING)
        #     if file_handler is not None:
        #         logger.addHandler(file_handler)
    else:
        pass


def traceback(logger: logging.Logger) -> str:
    msg = __traceback.format_exc()
    logger.error(msg)
    return msg


def getLogger(name: str = __name__, level: int = None, err_seperate=True, cls: ClassVar = None):
    from .logger import getLogger as getLoggers, Logger
    if level is None:
        from .logging import log_level
        level = log_level
    logger: Logger = getLoggers(name, cls=cls)
    # logger.parent = None
    logger.setLevel(level)
    addHandler(logger, name=name, level=level, err_seperate=err_seperate)
    return logger
