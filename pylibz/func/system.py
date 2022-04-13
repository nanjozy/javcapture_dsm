# -*- coding: utf-8 -*-
import os
import sys
import time
from functools import wraps


def set_env(key: str, value: str):
    os.environ[key] = value


def get_env(key: str):
    return os.environ.get(key)


def set_proxy(proxy: str):
    set_env("http_proxy", proxy)
    set_env("https_proxy", proxy)

    return get_env("http_proxy"), get_env("https_proxy")


def set_no_proxy(no_proxy: str):
    set_env("no_proxy", no_proxy)
    # os.environ.setdefault("no_proxy", no_proxy)
    return get_env("no_proxy")


def get_disk_free(folder: str) -> int:
    from psutil import disk_usage
    return disk_usage(folder).free


def getsizeof(obj, seen=None) -> int:
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([getsizeof(v, seen) for v in obj.values()])
        size += sum([getsizeof(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += getsizeof(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        size += sum([getsizeof(i, seen) for i in obj])
    return size


def try_except(return_error: bool = False, log_trace: bool = True):
    def func_wrapper(func):
        @wraps(func)
        def try_func(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_trace:
                    from ..logging import log
                    log().trace()
                if return_error:
                    return e
                return None

        return try_func

    return func_wrapper


def memory_usage() -> int:
    import psutil
    mem_process = psutil.Process(os.getpid()).memory_info().rss
    return round(mem_process / 1024 / 1024, 2)


def count_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        from ..logging import log
        start_time = time.time()
        try:
            return func(*args, **kwargs)
        finally:
            log().info("%s:\t%s ms", func.__name__, (time.time() - start_time) * 1000)

    return wrapper


def get_pid():
    return os.getpid()


def get_ram_use(pid: int):
    from psutil import Process
    return Process(pid).memory_info().rss


def get_ram_usable():
    from psutil import virtual_memory
    return virtual_memory().free


def get_cpu_use(interval: float = 1, percpu: bool = True):
    from psutil import cpu_percent
    return cpu_percent(interval, percpu=percpu)


def cpu_count() -> int:
    import multiprocessing
    return multiprocessing.cpu_count()


def get_process(pid: int):
    import psutil
    try:
        p: psutil.Process = psutil.Process(pid)
        return p
    except psutil.NoSuchProcess:
        return None


def kill(pid: int, safe: bool = True) -> bool:
    p = get_process(pid)
    if p is None:
        return False
    unsafe = False
    if safe:
        unsafe = True
        pid = get_pid()
        for t in p.parents():
            if t.pid == pid:
                unsafe = False
    if not unsafe:
        p.kill()
        return True
    else:
        return False


def in_uwsgi():
    return "UWSGI_ORIGINAL_PROC_NAME" in os.environ.keys()
