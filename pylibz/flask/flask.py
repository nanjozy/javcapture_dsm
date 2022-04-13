#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import timedelta
from pathlib import Path

from flask import Flask, jsonify as _jsonify, make_response
from werkzeug.middleware.proxy_fix import ProxyFix


def jsonify(obj, response=True):
    from ..util import JSONEncoder, jsonPreformat
    if response:
        return _jsonify(jsonPreformat(obj))
    else:
        return JSONEncoder().encode(obj)


def init_app() -> Flask:
    from ..setting import entry_name
    from ..func import in_uwsgi
    from .util import session_path, public_path, session_enabled, session_expired, flask_secret_key, cookie_prefix, \
        session_type
    f_params = dict(import_name=entry_name(), static_folder=public_path(), static_url_path='/')
    app = Flask(**f_params)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.secret_key = flask_secret_key()
    if session_enabled():
        from flask_session import Session
        if session_type() == "mongodb":
            from ..mongo import get_mongo_client, get_dbname
            app.config['SESSION_TYPE'] = 'mongodb'
            app.config['SESSION_MONGODB'] = get_mongo_client()
            app.config['SESSION_MONGODB_DB'] = get_dbname()
            app.config['SESSION_MONGODB_COLLECT'] = 'flask_session'
        else:
            app.config['SESSION_TYPE'] = 'filesystem'
            app.config['SESSION_FILE_DIR'] = session_path()
        app.config['SESSION_USE_SIGNER'] = True
        app.config['SESSION_REFRESH_EACH_REQUEST'] = True
        app.config['SESSION_KEY_PREFIX'] = cookie_prefix()
        app.config['SESSION_COOKIE_NAME'] = cookie_prefix().upper()
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(seconds=session_expired())
        Session(app)

    from .util import public_path
    index_path = Path(public_path(), "index.html").resolve()
    if index_path.is_file():
        with open(index_path.as_posix(), mode="rb") as f:
            index_bytes = f.read()

        @app.route('/', methods=['GET'])
        def catch_all():
            response = make_response(index_bytes)
            return response

    return app
