#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
from string import Template

from .util import JsonAble

__all__ = [
    "Errors",
    "Error",
    "NoneErr",
    "RuntimeErr",
    "DevErr",
    "NotFoundErr",
    "ParamErr",
    "ConfigErr",
    "LoginRequired",
    "AuthErr",
    "DuplicateErr",
]


class Errors(JsonAble, Exception):
    def __new__(cls, value: list):
        if isinstance(value, Errors):
            return value
        return super().__new__(cls, value=value)

    def __init__(self, value: list):
        if isinstance(value, Errors):
            return
        self.value = list(value)

    def __bool__(self):
        return len(self.value) <= 0

    def __str__(self):
        res = ""
        for errt in self.value:
            res += str(errt)
            res += "\n\n"
        return res


class Error(JsonAble, Exception):
    def __new__(cls, value=None, code: int = 500, err: Exception = None, trace: int = 0):
        if isinstance(err, Error):
            return err
        return super().__new__(cls, value=value, code=code, err=err, trace=trace)

    def __init__(self, value=None, code: int = 500, err: Exception = None, trace: int = 0):
        if isinstance(err, Error):
            return
        self.value = value
        self.code = code
        self.err = err
        self.trace_file, self.trace_line, self.trace_func = self.__getline(depth=trace + 2)
        if self.value is None and self.err is not None:
            self.value = format(self.err)
        self.isnone = False

    def get_value(self):
        return self.value

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, Error):
            return self.value == other.value
        else:
            return self.value == format(self.err)

    def __bool__(self):
        return not self.isnone

    def __str__(self):
        return "%s\tcode: %s\tFile \"%s:%s\", in %s\tvalue: %s\terr: %s" % (self.__class__.__name__,
                                                                            self.code, self.trace_file, self.trace_line,
                                                                            self.trace_func, self.value,
                                                                            self.err)

    def is_none(self) -> bool:
        return self.isnone

    def __getline(self, depth=2) -> (str, int, str):
        tracer = sys._getframe(depth)
        return tracer.f_code.co_filename, tracer.f_lineno, tracer.f_code.co_name


class NoneErr(Error):
    def __init__(self, value=None, code: int = 0, err: Exception = None, trace: int = 0):
        super().__init__(value, code=code, err=err, trace=trace + 1)
        self.isnone = True


class RuntimeErr(Error):
    def __new__(cls, value=None, code: int = 500, err: Exception = None, trace: int = 0):
        return super().__new__(cls, value=value, code=code, err=err, trace=trace)

    def __init__(self, value=None, code: int = 500, err: Exception = None, trace: int = 0):
        super().__init__(value=value, code=code, err=err, trace=trace + 1)


class DevErr(Error):
    def __init__(self, value=None, code: int = 501, err: Exception = None, trace: int = 0):
        super().__init__(value, code=code, err=err, trace=trace + 1)


NotFoundTpl = Template("${type}\t${value} not found ${situation}.")


class NotFoundErr(Error):
    def __init__(self, value=None, code: int = 404, err: Exception = None, trace: int = 0):
        super().__init__(value, code=code, err=err, trace=trace + 1)


class AuthErr(Error):
    def __init__(self, value=None, code: int = 403, err: Exception = None, trace: int = 0):
        super().__init__(value, code=code, err=err, trace=trace + 1)


class ParamErr(Error):
    def __new__(cls, value=None, code: int = 400, err: Exception = None, trace: int = 0):
        return super().__new__(cls, value=value, code=code, err=err, trace=trace)

    def __init__(self, value=None, code: int = 400, err: Exception = None, trace: int = 0):
        super().__init__(value, code=code, err=err, trace=trace + 1)


class DuplicateErr(ParamErr):
    pass


class ConfigErr(Error):
    def __init__(self, value=None, code: int = 500, err: Exception = None, trace: int = 0):
        super().__init__(value, code=code, err=err, trace=trace + 1)


class LoginRequired(Error):
    def __new__(cls, value=None, code: int = 401, err: Exception = None, trace: int = 0):
        return super().__new__(cls, value=value, code=code, err=err, trace=trace)

    def __init__(self, value=None, code: int = 401, err: Exception = None, trace: int = 0):
        super().__init__(value, code=code, err=err, trace=trace + 1)


class SSOLoginRequired(LoginRequired):
    def __new__(cls, value=None, code: int = 401, err: Exception = None, trace: int = 0):
        return super().__new__(cls, value=value, code=code, err=err, trace=trace)

    def __init__(self, value=None, code: int = 401, err: Exception = None, trace: int = 0):
        super().__init__(value=value, code=code, err=err, trace=trace + 1)


class LoginFail(LoginRequired):
    def __new__(cls, value=None, code: int = 400, err: Exception = None, trace: int = 0):
        return super().__new__(cls, value=value, code=code, err=err, trace=trace)

    def __init__(self, value=None, code: int = 400, err: Exception = None, trace: int = 0):
        super().__init__(value, code=code, err=err, trace=trace + 1)


class SSOException(Error):
    def __new__(cls, value=None, code: int = 403, err: Exception = None, trace: int = 0):
        return super().__new__(cls, value=value, code=code, err=err, trace=trace)

    def __init__(self, value=None, code: int = 403, err: Exception = None, trace: int = 0):
        super().__init__(value=value, code=code, err=err, trace=trace + 1)
