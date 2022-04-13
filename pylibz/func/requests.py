# -*- coding: utf-8 -*-
def dict_latin(obj: dict) -> dict:
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = dict_latin(value)
        return obj
    elif isinstance(obj, list):
        for i in range(len(obj)):
            obj[i] = dict_latin(obj[i])
        return obj
    elif isinstance(obj, str):
        obj = obj.encode("utf-8").decode("latin-1")
        return obj
    return obj


def basic_auth_header(username: str, password: str):
    from .encode import base64_encode
    auth = "%s:%s" % (username, password)
    return "Basic %s" % base64_encode(auth.encode("utf-8"))
