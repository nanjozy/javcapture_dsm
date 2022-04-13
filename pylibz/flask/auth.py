# -*- coding: utf-8 -*-

def auth_required():
    from .requests import Request
    from ..exceptions import LoginRequired
    auth = Request.authorization()
    if auth is None:
        raise LoginRequired()
    return auth.get("username"), auth.get("password")
