# -*- coding: utf-8 -*-
import json
from pylibz.func import ensure_folder
from pylibz import runtime, Path, log


def write_cache(tag: str, key: str, data: dict):
    try:
        path = Path(runtime(), tag, ).absolute()
        try:
            ensure_folder(path.as_posix())
        except:
            log().trace()
        path = path.joinpath("%s.json" % key)
        with open(path.as_posix(), "w+", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except:
        log().trace()


def get_cache(tag: str, key: str):
    try:
        path = Path(runtime(), tag, "%s.json" % key).absolute()
        if path.is_file():
            with open(path.as_posix(), "r", encoding="utf-8") as f:
                data = json.load(f)
                return data
        return None
    except:
        log().trace()
        return None
