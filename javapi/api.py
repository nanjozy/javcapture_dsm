#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pylibz.flask import error_handler, jsonify, make_response
from .javdb import search_javdb
from pylibz import log
from pylibz.func import base64_decode
import requests


def bind_router(app):
    @app.route('/javdb/<vid>', methods=['get'])
    def get_javdb(vid: str):
        try:
            log().info(vid)
            res = search_javdb(vid)
            if res is None:
                return jsonify({
                    "success": False,
                    "result": []
                })
            return jsonify(res)
        except:
            log().trace()
            return jsonify({
                "success": False,
                "result": []
            })

    @app.route('/javdb/img/<b64>', methods=['get'])
    def get_javdb_img(b64: str):
        b64 = base64_decode(b64)
        log().info(b64)
        response = requests.get(b64, headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36 Edg/100.0.1185.39"
        })
        res = make_response(response.content)
        res.content_type = "image/jpeg"
        return res

    error_handler(app)
