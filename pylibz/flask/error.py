# -*- coding: utf-8 -*-
import traceback
from typing import Callable


def error_handler(app, others: Callable = None):
    from .flask import jsonify
    from .libs import redirect
    from ..logging import log
    from ..exceptions import DuplicateErr, NotFoundErr, ParamErr, RuntimeErr, LoginRequired, AuthErr, SSOLoginRequired, \
        SSOException
    from werkzeug.exceptions import MethodNotAllowed
    from .requests import Request
    @app.errorhandler(404)
    def error_404(error):
        response = dict(code=0, path=Request.path(), msg="404 Not Found")
        return jsonify(response), 404

    @app.errorhandler(400)
    def error_400(error):
        response = dict(code=0, msg="请求错误", content=str(error))
        return jsonify(response), 400

    @app.errorhandler(SSOException)
    def error_SSOException(error):
        response = dict(code=403, content=format(error), msg="sso login fail")
        return jsonify(response), 500

    @app.errorhandler(SSOLoginRequired)
    def error_SSOLoginRequired(error):
        from ..sso.configs import get_portal_url, get_login_page
        response = dict(code=401, content=format(error), msg="sso login required")
        if get_portal_url():
            return redirect("/api/go_portal_login")
        return redirect(get_login_page())

    @app.errorhandler(Exception)
    def error_500(error):
        if callable(others):
            t = others(error)
            if t is None:
                pass
            else:
                return t

        if isinstance(error, LoginRequired):
            return 'Unauthorized', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'}
        elif isinstance(error, MethodNotAllowed):
            response = dict(code=0, content=format(error), msg="MethodNotAllowed")
            return jsonify(response), 404
        elif isinstance(error, DuplicateErr):
            log().info(traceback.format_exc())
            response = dict(code=0, content=error.value, msg="重复的键值")
            return jsonify(response), 400
        elif isinstance(error, ParamErr):
            log().info(traceback.format_exc())
            response = dict(code=0, msg="参数错误。", content=repr(error))
            return jsonify(response), 400
        elif isinstance(error, RuntimeErr):
            log().info(traceback.format_exc())
            response = dict(code=0, msg="运行时错误", content=repr(error))
            return jsonify(response), 500
        elif isinstance(error, NotFoundErr):
            log().info(traceback.format_exc())
            response = dict(code=0, msg=error.value, content=repr(error))
            return jsonify(response), 404
        elif isinstance(error, AuthErr):
            log().info(traceback.format_exc())
            response = dict(code=0, msg=error.value, content=repr(error))
            return jsonify(response), 403
        else:
            log().trace()
            response = dict(code=0, msg="500 Error", content=repr(error))
            return jsonify(response), 500
