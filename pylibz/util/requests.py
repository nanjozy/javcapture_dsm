# -*- coding: utf-8 -*-
import requests

from ..func import json, sleep


def request(method: str, url: str, headers: dict = None, data: dict = None, retry: int = 5, retry_delay: int = 5,
            **kwargs):
    from ..logging import log
    if isinstance(data, dict):
        data = json.dumps(data, ensure_ascii=False)
        data = data.encode("utf-8").decode("latin1")
    if retry < 1:
        retry = 1
    req_args = dict(verify=False)
    if headers is not None:
        req_args["headers"] = headers
    if data is not None:
        req_args["data"] = data
    req_args.update(kwargs)
    for i in range(retry):
        response = requests.request(method, url, **req_args)
        if 300 > response.status_code >= 200:
            return response
        elif response.status_code in (404, 502):
            log().warning("request fail, code:%s, content:%s", response.status_code, response.text)
            if i >= retry - 1:
                return response
            sleep(retry_delay)
        else:
            return response
    return response
