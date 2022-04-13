# -*- coding: utf-8 -*-
import base64
import hashlib
from typing import Union


def base64_encode(b: Union[bytes, str], altchars: bytes = None):
    if isinstance(b, str):
        b = b.encode("utf-8")
    if isinstance(altchars, str):
        altchars = altchars.encode("utf-8")
    s = base64.b64encode(b, altchars=altchars)
    s = s.decode("utf-8")
    return s


def base64_decode(b: str, altchars: bytes = None, validate=False):
    if isinstance(altchars, str):
        altchars = altchars.encode("utf-8")
    return base64.b64decode(b, altchars=altchars, validate=validate)


def md5(s: Union[str, bytes], encoding: str = "utf-8") -> str:
    if isinstance(s, str):
        s = s.encode(encoding=encoding)
    return hashlib.md5(s).hexdigest()


def etag_format(etag: str) -> str:
    if etag is None:
        return etag
    return etag.lower().strip("\"")
