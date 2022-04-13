# -*- coding: utf-8 -*-
from types import FunctionType, MethodType
from typing import Callable


def function_params(func: Callable) -> list:
    if isinstance(func, type) and hasattr(func, "__init__") and callable(func.__init__):
        func = func.__init__
        if isinstance(func, (FunctionType, MethodType)):
            params = list(func.__code__.co_varnames)
            params.pop(0)
        else:
            return []
    else:
        assert isinstance(func, (FunctionType, MethodType)), "%r" % func
        params = list(func.__code__.co_varnames)
        if isinstance(func, (MethodType)):
            params.pop(0)
        elif isinstance(func, FunctionType):
            pass
    return params


def safe_call(func: Callable, *args, **kwargs):
    params = function_params(func)
    args = args[:len(params)]
    for i in range(len(args)):
        params.pop(0)
    kwargs2 = dict()
    for k, v in kwargs.items():
        if k in params:
            kwargs2[k] = v
    return func(*args, **kwargs2)


def safe_call_k(func: Callable, *args, **kwargs):
    params = function_params(func)
    args = args[:len(params)]
    kwargs2 = dict()
    for i, v in enumerate(args):
        kwargs2[params[i]] = v
    for k, v in kwargs.items():
        if k in params:
            kwargs2[k] = v
    return func(**kwargs2)


def deep_equal(a, b) -> bool:
    if type(a) != type(b):
        return False
    if isinstance(a, (tuple, list)):
        if len(a) != len(b):
            return False
        for i, v in enumerate(a):
            if deep_equal(v, b[i]):
                pass
            else:
                return False
        return True
    elif isinstance(a, dict):
        if len(a) != len(b):
            return False
        for k in a.keys():
            if k not in b.keys():
                return False
            if deep_equal(a[k], b[k]):
                pass
            else:
                return False
        return True
    else:
        return a == b
