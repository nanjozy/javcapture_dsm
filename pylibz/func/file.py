# -*- coding: utf-8 -*-
import os
from typing import Generator, Union

from .libs import Path


def split_path(filename: str) -> (str, str, str):
    path = Path(filename)
    ext = path.suffix
    folder = path.parent
    name = path.name[0:len(path.name) - len(ext)]
    return str(folder), str(name), str(ext)


def ensure_folder(path: Union[Path, str], mode: int = 0o1777):
    if isinstance(path, Path):
        path = path.as_posix()
    os.makedirs(path, mode=mode, exist_ok=True)


def cloud_path(*path: str) -> str:
    p = Path(*path).as_posix().strip("/")
    if len(p):
        p = p + "/"
    return p


def get_size(file: str) -> int:
    try:
        return os.path.getsize(file)
    except FileNotFoundError:
        return None


def du(path: str, file_only: bool = False) -> Generator[Path, None, None]:
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            yield Path(root, name)
        if not file_only:
            for name in dirs:
                yield Path(root, name)


def getctime(path: str):
    from .time_func import timestap2datetime
    return timestap2datetime(os.path.getctime(path))


def getmtime(path: str):
    from .time_func import timestap2datetime
    return timestap2datetime(os.path.getmtime(path))


def touch(file: str):
    with open(file, mode="w") as f:
        f.close()


def del_path(path: str):
    for root, dirs, files in os.walk(path, topdown=False):
        for f in files:
            f = Path(root, f)
            del_file(f.as_posix())
        for f in dirs:
            f = Path(root, f)
            del_folder(f.as_posix())


def del_file(file: str):
    from ..logging import log
    try:
        os.remove(file)
    except Exception as e:
        log().warning(format(e))


def del_folder(folder: str):
    from ..logging import log
    try:
        os.rmdir(folder)
    except Exception as e:
        log().warning(format(e))


def get_tmp_path(*args) -> Path:
    from ..setting import runtime
    return Path(runtime(), *args).absolute()


def absolute_path(path: str) -> Path:
    path = path.strip()
    if path[:2] == "./":
        from ..setting import root
        path = Path(root(), path[2:]).absolute()
        return path
    else:
        return Path(path).absolute()
