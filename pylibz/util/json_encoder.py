# -*- coding: utf-8 -*-
import datetime
import json
from pathlib import Path


def jsonPreformat(o):
    from .json_able import JsonAble

    if isinstance(o, JsonAble):
        return jsonPreformat(o.to_dict())
    elif isinstance(o, datetime.datetime):
        return datetime.datetime.strftime(o, '%Y-%m-%d %H:%M:%S')
    elif isinstance(o, datetime.date):
        return datetime.date.strftime(o, '%Y-%m-%d %H:%M:%S')
    elif isinstance(o, set):
        return list(o)
    elif isinstance(o, Path):
        return str(o)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            o[i] = jsonPreformat(v)
        return o
    elif isinstance(o, dict):
        for i in o.keys():
            o[i] = jsonPreformat(o[i])
        return o
    elif type(o) == "<class 'bson.objectid.ObjectId'>":
        from bson import ObjectId
        if isinstance(o, ObjectId):
            return jsonPreformat(str(o))

    if hasattr(o, "to_dict") and callable(o.to_dict):
        return jsonPreformat(o.to_dict())
    elif hasattr(o, "keys") and hasattr(o, "__getitem__"):
        return jsonPreformat(dict(o))
    elif callable(o):
        res = "#method#"
        return res
    return o


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        from .cloud_file import CloudFile
        from .json_able import JsonAble

        if isinstance(o, JsonAble):
            return o.to_dict()
        elif isinstance(o, datetime.datetime):
            return datetime.datetime.strftime(o, '%Y-%m-%d %H:%M:%S')
        elif isinstance(o, set):
            return list(o)
        elif isinstance(o, CloudFile):
            return dict(vars(o))
        elif isinstance(o, Path):
            return str(o)
        elif type(o) == "<class 'bson.objectid.ObjectId'>":
            from bson import ObjectId
            if isinstance(o, ObjectId):
                return str(o)
        if hasattr(o, "to_dict") and callable(o.to_dict):
            return o.to_dict()
        elif hasattr(o, "keys") and hasattr(o, "__getitem__"):
            return dict(o)
        return json.JSONEncoder.default(self, o)
