# -*- coding: utf-8 -*-
import os
from logging import addLevelName, DEBUG, ERROR, FATAL, getLogger as getLoggerCore, INFO, Logger as LoggerCore, NOTSET, \
    WARNING
from traceback import format_exc
from typing import ClassVar

_srcfile = os.path.normcase(addLevelName.__code__.co_filename)

addLevelName(5, "DEVELOP")
addLevelName(1, "TRACK")
addLevelName(35, "TRACKBACK")


class Logger(LoggerCore):
    # def __init__(self, name, level=NOTSET):
    #     super(Logger, self).__init__(name, level=level)
    #     self.trace_level=1
    #
    # def trace(self,level:int=None):
    NOTSET = NOTSET
    DEVELOP = 5
    TRACK = 1
    DEBUG = DEBUG
    INFO = INFO
    WARNING = WARNING
    ERROR = ERROR
    TRACE = 35
    FATAL = FATAL

    def print(self, *args, formats: str = "%s", delimeter: str = "\t"):
        msg = ""
        for arg in args:
            if msg:
                msg += delimeter
            msg += formats % arg
        print(msg)

    def trace(self, level: int = WARNING, limit=None, chain=True):
        self._log(level, format_exc(limit=limit, chain=chain), (), )

    def dev(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.DEVELOP):
            self._log(self.DEVELOP, msg, args, **kwargs)

    def devln(self, *args, formats: str = "%s", delimeter: str = "\n>>>>>>\n"):
        msg = ""
        for arg in args:
            if msg:
                msg += delimeter
            msg += formats % arg
        if self.isEnabledFor(self.DEVELOP):
            self._log(self.DEVELOP, msg, (), )

    def track(self, msg, *args, **kwargs):
        if self.isEnabledFor(self.TRACK):
            self._log(self.TRACK, msg, args, **kwargs)

    def trackln(self, *args, formats: str = "%s", delimeter: str = "\n>>>>>>\n"):
        msg = ""
        for arg in args:
            if msg:
                msg += delimeter
            msg += formats % arg
        if self.isEnabledFor(self.TRACK):
            self._log(self.TRACK, msg, (), )

    def debugln(self, *args, formats: str = "%s", delimeter: str = "\n>>>>>>\n"):
        msg = ""
        for arg in args:
            if msg:
                msg += delimeter
            msg += formats % arg
        if self.isEnabledFor(DEBUG):
            self._log(DEBUG, msg, (), )

    def warningln(self, *args, formats: str = "%s", delimeter: str = "\n>>>>>>\n"):
        msg = ""
        for arg in args:
            if msg:
                msg += delimeter
            msg += formats % arg
        if self.isEnabledFor(WARNING):
            self._log(WARNING, msg, (), )

    def jsonln(self, *args, level: int = INFO, formats: str = "%s", delimeter: str = "\n>>>>>>\n", indent: int = 4):
        msg = ""
        for arg in args:
            from ..util import JsonAble
            from ..func import jsondumps
            if msg:
                msg += delimeter
            if isinstance(arg, (list, dict, JsonAble)):
                arg = jsondumps(arg, indent=indent)
            msg += formats % arg
        if self.isEnabledFor(level):
            self._log(level, msg, (), )

    def infoln(self, *args, formats: str = "%s", delimeter: str = "\n>>>>>>\n"):
        msg = ""
        for arg in args:
            if msg:
                msg += delimeter
            msg += formats % arg
        if self.isEnabledFor(INFO):
            self._log(INFO, msg, (), )

    def errorln(self, *args, formats: str = "%s", delimeter: str = "\n>>>>>>\n"):
        msg = ""
        for arg in args:
            if msg:
                msg += delimeter
            msg += formats % arg
        if self.isEnabledFor(ERROR):
            self._log(ERROR, msg, (), )

    def fataln(self, *args, formats: str = "%s", delimeter: str = "\n>>>>>>\n"):
        msg = ""
        for arg in args:
            if msg:
                msg += delimeter
            msg += formats % arg
        if self.isEnabledFor(FATAL):
            self._log(FATAL, msg, (), )

    # def findCaller(self, stack_info=False):
    #     """
    #             Find the stack frame of the caller so that we can note the source
    #             file name, line number and function name.
    #             """
    #     f = currentframe()
    #     # On some versions of IronPython, currentframe() returns None if
    #     # IronPython isn't run with -X:Frames.
    #     if f is not None:
    #         f = f.f_back
    #     rv = "(unknown file)", 0, "(unknown function)", None
    #     print(f, sys._getframe(0))
    #     while hasattr(f, "f_code"):
    #         co = f.f_code
    #         filename = os.path.normcase(co.co_filename)
    #         if filename == _srcfile:
    #             f = f.f_back
    #             continue
    #         sinfo = None
    #         if stack_info:
    #             sio = io.StringIO()
    #             sio.write('Stack (most recent call last):\n')
    #             traceback.print_stack(f, file=sio)
    #             sinfo = sio.getvalue()
    #             if sinfo[-1] == '\n':
    #                 sinfo = sinfo[:-1]
    #             sio.close()
    #         rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
    #         break
    #     return rv


def getLogger(name: str, cls: ClassVar = None) -> Logger:
    logger = getLoggerCore(name)
    if cls is None:
        cls = Logger
    assert issubclass(cls, Logger)
    log = cls(logger.name, level=logger.level)
    log.parent = logger.parent
    log.propagate = logger.propagate
    log.handlers = logger.handlers
    log.disabled = logger.disabled
    log.filters = logger.filters
    return log
