# -*- coding: utf-8 -*-
import datetime

__all__ = [
    "TIMEZONE",
    "TIMEZONE_UTC",
    "ZERO_TIME",
    "TIMEZONE_pytz",
    "VERSION",
]
TIMEZONE = datetime.timezone(datetime.timedelta(hours=8))

VERSION = 12


def TIMEZONE_pytz():
    import pytz
    return pytz.timezone('Asia/Shanghai')


TIMEZONE_UTC = datetime.timezone.utc
ZERO_TIME = datetime.datetime.fromtimestamp(0)
