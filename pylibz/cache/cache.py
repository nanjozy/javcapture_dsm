# -*- coding: utf-8 -*-


from typing import Dict

from ..func import datetime, get_now, in_uwsgi, timedelta
from ..logging import log


class C:
    def __init__(self, value: str, expire_date: datetime):
        self.value = value
        self.expire_date = expire_date

    def is_expired(self):
        if get_now() > self.expire_date:
            return True
        return False


class G:
    def __init__(self):
        self.cache: Dict[str, C] = {}

    def cache_update(self, key: str, value, expires):
        self.cache[key] = C(value=value, expire_date=get_now() + timedelta(seconds=expires))
        for k in list(self.cache.keys()):
            if self.cache[k].is_expired():
                if k in self.cache.keys():
                    del self.cache[k]
        return True

    def cache_get(self, key: str):
        res = self.cache.get(key)
        if not isinstance(res, C):
            return None
        if res.is_expired():
            if key in self.cache.keys():
                del self.cache[key]
            return None
        return res.value

    def cache_clear(self):
        self.cache = {}


g = None


def gcache():
    global g
    if g is None:
        g = G()
    return g


class UCache:
    @classmethod
    def set(cls, key: str, value, expires: int = 0):
        try:
            if in_uwsgi():
                from ..flask import uwsgi_cache_enabled
                if uwsgi_cache_enabled():
                    import uwsgi
                    import dill
                    value = dill.dumps(value)
                    uwsgi.cache_update(key, value, expires)
                    return
            cache = gcache()
            cache.cache_update(key, value, expires)
        except:
            log().trace()

    @classmethod
    def clear(cls):
        try:
            if in_uwsgi():
                from ..flask import uwsgi_cache_enabled
                if uwsgi_cache_enabled():
                    import uwsgi
                    uwsgi.cache_clear()
                    return
            gcache().cache_clear()
        except:
            log().trace()

    @classmethod
    def get(cls, key: str):
        try:
            if in_uwsgi():
                from ..flask import uwsgi_cache_enabled
                if uwsgi_cache_enabled():
                    import uwsgi, dill
                    value = uwsgi.cache_get(key)
                    if value is not None:
                        value = dill.loads(value)
                    return value
            cache = gcache()
            value = cache.cache_get(key)
            return value
        except:
            log().trace()
            return None


class Cache:
    @classmethod
    def get_key(cls, tag: str, key: str, ):
        return "T:%s#K:%s" % (tag, key,)

    @classmethod
    def set(cls, tag: str, key: str, value, expires: int = 60, **kwargs):
        try:
            UCache.set(cls.get_key(tag, key), value, expires=expires)
        except:
            log().trace()

    @classmethod
    def get(cls, tag: str, key: str, **kwargs):
        try:
            obj = UCache.get(cls.get_key(tag, key))
            if obj is not None:
                return obj
        except:
            log().trace()
        return None

    @classmethod
    def clear(cls, **kwargs):
        try:
            UCache.clear()
        except:
            log().trace()
