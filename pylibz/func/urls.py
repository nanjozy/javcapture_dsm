# -*- coding: utf-8 -*-


def get_domain(url: str):
    from urllib3.util import parse_url
    url = parse_url(url)
    port = url.port
    if port is None:
        if url.scheme is None:
            port = 443
        elif url.scheme.lower() == "http":
            port = 80
        elif url.scheme.lower() == "https":
            port = 443
        else:
            port = 443
    return "%s:%s" % (url.host, port)
