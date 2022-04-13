# -*- coding: utf-8 -*-
from urllib.parse import urlparse

from flask import request, session


class Request:
    def __init__(self):
        pass

    @classmethod
    def remote_addr(cls, ) -> str:
        return request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

    @classmethod
    def session(cls):
        return session

    @classmethod
    def authorization(cls):
        return request.authorization

    @classmethod
    def g(cls, key: str, default=None):
        gt = cls.get_g()
        if gt is None:
            return default
        if hasattr(gt, key):
            return getattr(gt, key)
        return default

    @classmethod
    def get_g(cls):
        g = None
        try:
            from flask import g as _g, current_app
            _ = current_app.name
            g = _g
        except:
            pass
        return g

    @classmethod
    def url(cls):
        return request.url

    @classmethod
    def path(cls):
        return request.path

    @classmethod
    def url_rule(cls):
        return str(request.url_rule)

    @classmethod
    def headers(cls):
        return dict(request.headers)

    @classmethod
    def view_args(cls):
        return dict(request.view_args)

    @classmethod
    def args(cls):
        return request.args

    @classmethod
    def gets(cls):
        from .data import Request as Req
        return Req.get_query()

    @classmethod
    def posts(cls):
        from .data import Request as Req
        return Req.get_request()

    @classmethod
    def method(cls):
        return request.method.upper()

    @classmethod
    def query(cls):
        return request.values.to_dict()

    @classmethod
    def data(cls) -> bytes:
        return request.data

    @classmethod
    def scheme(cls) -> str:
        return request.scheme.lower()

    @classmethod
    def base_url(cls):
        return "%s://%s" % (cls.scheme(), cls.host())

    @classmethod
    def host(cls) -> str:
        return request.host

    @classmethod
    def port(cls) -> int:
        return urlparse(Request.url()).port

    @classmethod
    def endpoint(cls):
        return request.endpoint

    @classmethod
    def cookies(cls):
        return request.cookies

    @classmethod
    def get_user(cls):
        auth = cls.authorization()
        if auth is None:
            return None
        return auth.get("username")
