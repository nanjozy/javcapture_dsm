# -*- coding: utf-8 -*-
import datetime
import gzip
import os
import re
from pathlib import Path

from .logging import log

GC_SIZE = 10 * 1024 * 1024
GC_ROTATE = 600
GC_DELTA = datetime.timedelta(days=1)
TMP_SUFFIX = ".logtmp"
date_re = re.compile(r"\.\d{4}-\d{2}-\d{2}\.")


def gc_log():
    try:
        _gc_log()
    except:
        log().trace()


# def gc_current_log():
#     try:
#         log().track("gc_current_log")
#         from ..setting import log_path
#         from ..func import get_size, get_now, in_uwsgi, get_date_start
#         GC_DATE = get_date_start(get_now())
#         for root, dirs, files in os.walk(log_path(), topdown=False):
#             for f in files:
#                 f = Path(root, f).absolute()
#                 suffix = f.suffix
#                 if suffix not in (".txt", ".log", TMP_SUFFIX):
#                     continue
#                 f = f.as_posix()
#                 if suffix == TMP_SUFFIX:
#                     gc_file(f)
#                 elif get_log_time(f) <= GC_DATE:
#                     gc_file(f)
#                 elif suffix == ".log" and get_size(f) > 1024 * 10:
#                     gc_file(f)
#     except:
#         log().trace()


def _gc_log():
    from ..setting import log_path
    from ..func import get_size, get_now, get_date_start
    now = get_now()
    GC_DATE = get_date_start(now)
    for root, dirs, files in os.walk(log_path(), topdown=False):
        for f in files:
            f = Path(root, f).absolute()
            suffix = f.suffix
            if suffix not in (".txt", TMP_SUFFIX):
                continue
            f = f.as_posix()
            if get_size(f) >= GC_SIZE:
                gc_file(f)
            elif get_log_time(f) < GC_DATE:
                gc_file(f)


def gc_file(file: str):
    from ..setting import on_windows
    if on_windows():
        return
    from ..func import get_size
    try:
        log().track("back log %s", file)
        f = Path(file)
        suffix = f.suffix
        if get_size(file) < 1:
            # log().debug("remove %s", file)
            os.remove(file)
            # if suffix == ".log":
            #     touch_log(f.as_posix())
            return
        if not f.exists():
            # log().debug("file not found %s", file)
            return
        if suffix == TMP_SUFFIX:
            target = f.with_suffix("").as_posix()
            current = f.as_posix()
        else:
            dir = f.parent
            name = f.with_suffix("").name
            if match_time(f.as_posix()):
                target_tpl = dir.joinpath(name + "_{num}" + suffix).as_posix()
            else:
                ctime = get_log_time(f.as_posix())
                target_tpl = ".{c}".format(c=ctime.strftime("%Y-%m-%d"))
                target_tpl += "_{num}"
                target_tpl = dir.joinpath(name + target_tpl + suffix).as_posix()
            i = 0
            while True:
                t = target_tpl.format(num=i)
                if Path(t + ".gz").exists():
                    pass
                elif Path(t + TMP_SUFFIX).exists():
                    pass
                else:
                    target = t
                    break
                i += 1
            current = target + TMP_SUFFIX
            f.rename(current)
            # if suffix == ".log":
            #     touch_log(f.as_posix())
        with gzip.open(target + ".gz", mode="wb") as gz:
            with open(current, mode="rb") as fp:
                while True:
                    row = fp.readline()
                    if len(row) < 1:
                        break
                    gz.write(row)
        os.remove(current)
    except:
        log().trace()


# def touch_log(file: str):
#     from ..setting import config, root
#     from ..func import touch, in_uwsgi
#     if not in_uwsgi():
#         return
#     while not os.path.exists(file):
#         path = config("main").get("log_touch")
#         if path is None:
#             path = Path(root(), "ulog.touch").as_posix()
#         touch(path)
#         time.sleep(1)


def match_time(file: str):
    res = date_re.findall(file)
    return len(res) > 0


def get_log_time(file: str):
    res = date_re.findall(file)
    if len(res) < 1:
        from ..func import getctime
        return getctime(file)
    else:
        from ..func import timestr2datetime
        res = res.pop().strip(".")
        res = timestr2datetime(res, "%Y-%m-%d")
        return res
