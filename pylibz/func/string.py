# -*- coding: utf-8 -*-
import re
import string
import uuid as _uuid
from secrets import token_hex, token_urlsafe
from typing import Union


def str_tpl(tpl: str, *args, **kws) -> str:
    return string.Template(tpl).substitute(*args, **kws)


def render_template(template: str, *args, **kws) -> str:
    s = string.Template(template)
    return s.substitute(*args, **kws)


def bytes_mode(a: int, b: int) -> int:
    c = (a - b) % 36
    if c < 10:
        c = c + 48
    else:
        c = c + 87
    return c


def uuid() -> str:
    u = _uuid.uuid5(_uuid.uuid1(), str(_uuid.uuid4()))
    return str(u)


def object_id():
    from .time_func import get_now
    from bson import ObjectId
    return "%s%s" % (get_now().strftime("%y%m%d%H%M%S"), str(ObjectId())[4:])


def buuid() -> str:
    u = uuid()
    u = u.encode("utf-8")
    n = bytearray()
    l = int(len(u) / 2)
    for i in range(l):
        ii = i * 2
        n.append(bytes_mode(u[ii], u[ii + 1]))
    n = n.decode("utf-8")
    return n


def suid(length: int = 18) -> str:
    t1, t2 = token_hex(nbytes=1)
    token = token_urlsafe(nbytes=length)
    token = token.replace("_", t1).replace("-", t2)
    while len(token) < length:
        token += token
    token = token[:length]
    return token


def tuid() -> str:
    from .time_func import get_now
    return "{time}{uuid}".format(time=get_now().strftime("%y%m%d%H%M%S"), uuid=suid(length=18))


control_chars = ''.join(map(chr, list(range(0, 32)) + list(range(127, 160))))
control_char_re = re.compile('[%s]' % re.escape(control_chars))


def str_clear(s: str) -> str:
    global control_char_re
    s = control_char_re.sub(" ", s)
    return s.strip()


def size_to_str(size: Union[int, float]) -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    p = 1024
    for i in range(len(units)):
        if (size / p) < 1:
            return "%.2f %s" % (size, units[i])
        size = size / p
