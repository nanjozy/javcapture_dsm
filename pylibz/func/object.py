# -*- coding: utf-8 -*-
from copy import deepcopy


def merge_dict(obj: dict, *args, deep_copy: bool = True):
    if deep_copy:
        obj = deepcopy(obj)
    if len(args):
        args = list(args)
        t = args.pop(0)
        if deep_copy:
            t = deepcopy(t)
        for k, v in t.items():
            if k in obj.keys():
                if isinstance(obj[k], dict):
                    obj[k] = merge_dict(obj[k], v, deep_copy=deep_copy)
                    continue
            obj[k] = v
    if len(args):
        obj = merge_dict(obj, *args, deep_copy=deep_copy)
    return obj


def del_key(obj: dict, key: str):
    if key in obj.keys():
        del obj[key]
    return obj
