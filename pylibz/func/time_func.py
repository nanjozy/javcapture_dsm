# -*- coding: utf-8 -*-
import datetime

from ..statics import TIMEZONE


def get_now(tz=None) -> datetime.datetime:
    if tz is None:
        tz = TIMEZONE
    return datetime.datetime.now(tz=tz)


def get_date(delta: int = 0, tz=None) -> datetime.datetime:
    if tz is None:
        tz = TIMEZONE
    return datetime.datetime(*datetime.datetime.now(tz=tz).date().timetuple()[:6]).astimezone(
        tz=tz) + datetime.timedelta(
        days=delta)


def get_date_start(date: datetime.datetime, tz=None) -> datetime.datetime:
    if tz is None:
        tz = TIMEZONE
    date = date.astimezone(tz=tz)
    return datetime.datetime(*date.date().timetuple()[:6]).astimezone(
        tz=tz)


def timezone_format(date: datetime.datetime, default_tzinfo=TIMEZONE, tzinfo=TIMEZONE) -> datetime.datetime:
    if date.tzinfo is None:
        date = date.replace(tzinfo=default_tzinfo)
    date = date.astimezone(tz=tzinfo)
    return date


def datetime2timestap(date: datetime) -> int:
    return int(date.timestamp())


def datetime2timestapf(date: datetime.datetime) -> float:
    return date.timestamp()


def timestap2datetime(timestap: float) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestap, tz=TIMEZONE)


def utc2datetime(timestr: str, formats: str = None) -> datetime.datetime:
    if formats is None:
        try:
            res = datetime.datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            res = datetime.datetime.strptime(timestr, "%Y-%m-%dT%H:%M:%SZ")
    else:
        res = datetime.datetime.strptime(timestr, formats)
    res = res + datetime.timedelta(hours=8)
    res = res.strftime("%Y-%m-%d %H:%M:%S.%f")
    res = timestr2datetime(res, "%Y-%m-%d %H:%M:%S.%f")
    return res


def gmt2datetime(timestr: str, formats: str = "%a, %d %b %Y %H:%M:%S GMT") -> datetime.datetime:
    return timestr2datetime(timestr, formats)


def timestr2datetime(timestr: str, formats: str) -> datetime.datetime:
    date: datetime.datetime = datetime.datetime.strptime(timestr, formats)
    date = timezone_format(date)
    return date


def date_format_replace(date: datetime.datetime, fmt: str, default_fmt: str = "%Y-%m-%d %H:%M:%S"):
    date = date.strftime(fmt)
    return timestr2datetime(date, default_fmt)


def get_biz_date(frequency: str, base_time: datetime = None) -> str:
    from ..exceptions import RuntimeErr
    if base_time is None:
        base_time = get_now()
    frequency = frequency.upper()
    if frequency == 'YEARLY':
        return str(base_time.year - 1)
    elif frequency == 'MONTHLY':
        return (base_time.replace(day=1) - datetime.timedelta(days=1)).strftime("%Y%m")
    elif frequency == 'WEEKLY':
        return (base_time - datetime.timedelta(days=base_time.weekday() + 7)).strftime("%Y%m%d")
    elif frequency == 'DAILY':
        return (base_time - datetime.timedelta(days=1)).strftime("%Y%m%d")
    elif frequency == 'HOURLY':
        return (base_time - datetime.timedelta(hours=1)).strftime("%Y%m%d%H")
    raise RuntimeErr("Not a valid frequency definition: " + frequency)


def month_in_season(date: datetime.datetime) -> int:
    month = date.month
    return month % 3
