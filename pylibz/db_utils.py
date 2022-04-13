# -*- coding: utf-8 -*-
def field_enc(key: str, obj):
    from .crypt import aes_enc
    obj = aes_enc(key, obj, compress=True)
    obj = "$\v{}\v#".format(obj)
    return obj


def field_dec(key: str, obj):
    from .crypt import aes_dec
    if len(obj) > 4 and len(obj) % 4 == 4 and obj[:2] == "$\v" and obj[-2:] == "\v#":
        obj = obj[2:len(obj) - 2]
        obj = aes_dec(key, obj)
    return obj
