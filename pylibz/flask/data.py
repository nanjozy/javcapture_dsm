#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import datetime
from functools import wraps
from typing import ClassVar, Dict, List, Union

from flask import request as _request
from werkzeug.datastructures import FileStorage, ImmutableMultiDict
from werkzeug.utils import secure_filename

from ..exceptions import ParamErr
from ..logging import log
from ..statics import TIMEZONE
from ..util import JsonAble


class ValidateType(ABC, JsonAble):
    @abstractmethod
    def validate(self, obj, key: str) -> bool:
        pass

    @classmethod
    def skip_none(cls, func):
        @wraps(func)
        def __skip(clss, obj, key):
            if key not in obj.keys():
                return True
            return func(clss, obj, key)

        return __skip


class Default(ValidateType):
    def __init__(self, default=None):
        self.default = default

    def validate(self, obj, key: str) -> bool:
        if key not in obj.keys():
            obj[key] = deepcopy(self.default)
        return True


class Required(ValidateType):
    def __init__(self):
        pass

    def validate(self, obj, key: str) -> bool:
        if key not in obj.keys():
            return self.throw(key)
        else:
            return True

    def throw(self, key: str) -> bool:
        raise ParamErr("缺失参数%s。" % key)


class Type(ValidateType):
    def __init__(self, *value: ClassVar, force: bool = True):
        self.value = value
        self.force = force

    @ValidateType.skip_none
    def validate(self, obj, key: str) -> bool:
        for typec in self.value:
            if isinstance(obj[key], typec):
                return True
        if self.force and len(self.value) == 1:
            try:
                obj[key] = self.value[0](obj[key])
                return True
            except Exception as e:
                from ..logging import log
                log().trace()
                return self.throw(key)
        else:
            return self.throw(key)

    def throw(self, key: str) -> bool:
        raise ParamErr("参数%s不为%s类型." % (key, self.value))


class Json(ValidateType):
    def __init__(self, transfer: bool = True):
        self.transfer = transfer

    @ValidateType.skip_none
    def validate(self, obj, key: str) -> bool:
        if isinstance(obj[key], (dict, list)):
            return True
        if self.transfer and isinstance(obj[key], str) and obj.get(key):
            try:
                obj[key] = json.loads(obj[key])
                return True
            except Exception as e:
                return self.throw(key)
        else:
            return self.throw(key)

    def throw(self, key: str) -> bool:
        raise ParamErr("参数%sJSON校验失败." % (key,))


class Boolean(ValidateType):
    def __init__(self, transfer: bool = True):
        self.transfer = transfer

    @ValidateType.skip_none
    def validate(self, obj, key: str) -> bool:
        if isinstance(obj[key], bool):
            return True
        if self.transfer and key in obj.keys():
            try:
                t = obj[key]
                if isinstance(t, int):
                    if t == 0:
                        t = False
                    else:
                        t = True
                elif isinstance(t, str):
                    t = t.lower()
                    if t == "true" or t == "1":
                        t = True
                    elif t == "false" or t == "0":
                        t = False
                    else:
                        raise ParamErr("unkown bool type t %s" % t)
                else:
                    raise ParamErr("unkown bool type t %s" % t)
                obj[key] = t
                return True
            except Exception as e:
                return self.throw(key)
        else:
            return self.throw(key)

    def throw(self, key: str) -> bool:
        raise ParamErr("参数%s Bool校验失败." % (key,))


class Date(ValidateType):
    def __init__(self, fmt: str = None, transfer: bool = True):
        if fmt is None:
            fmt = "%Y-%m-%d %H:%M:%S"
        self.fmt = fmt
        self.transfer = transfer

    @ValidateType.skip_none
    def validate(self, obj, key: str) -> bool:
        if isinstance(obj[key], datetime):
            return True
        if self.transfer and isinstance(obj[key], str) and obj.get(key):
            try:
                obj[key] = datetime.strptime(obj.get(key), self.fmt).astimezone(tz=TIMEZONE)
                return True
            except Exception as e:
                return self.throw(key)
        else:
            return self.throw(key)

    def throw(self, key: str) -> bool:
        raise ParamErr("参数%s校验失败." % (key,))


class Range(ValidateType):
    def __init__(self, min: int = None, max: int = None):
        self.min = min
        self.max = max

    @ValidateType.skip_none
    def validate(self, obj, key: str) -> bool:
        if isinstance(obj[key], str) or isinstance(obj[key], list) or isinstance(obj[key], dict):
            size = len(obj[key])
        else:
            size = obj[key]
        if self.min is not None:
            if size < self.min:
                return self.throw(key)
        if self.max is not None:
            if size > self.max:
                return self.throw(key)
        return True

    def throw(self, key: str) -> bool:
        if self.min and self.max:
            raise ParamErr("参数%s不在范围%s - %s内." % (key, self.min, self.max))
        elif self.min:
            raise ParamErr("参数%s需要大于%s." % (key, self.min))
        elif self.max:
            raise ParamErr("参数%s需要小于%s." % (key, self.max))
        return True


class In(ValidateType):
    def __init__(self, lists: list):
        self.lists = lists

    @ValidateType.skip_none
    def validate(self, obj, key: str) -> bool:
        if obj[key] in self.lists:
            return True
        else:
            return self.throw(key)

    def throw(self, key: str) -> bool:
        raise ParamErr("参数%s不在范围%r内." % (key, self.lists,))


class IsFile(ValidateType):
    def __init__(self, exts: List[str] = None):
        self.exts = exts

    @ValidateType.skip_none
    def validate(self, obj, key: str) -> bool:
        tmp = obj[key]
        if not isinstance(tmp, list):
            tmp = [tmp]
        for filet in tmp:
            if not isinstance(filet, FileStorage):
                return self.throw(key)
            if self.exts is not None and not self.__allowed_file(filet.filename):
                return self.throw_exts(key)
        return False

    def __allowed_file(self, filename, ):
        if self.exts is None:
            return True
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.exts

    def throw(self, key: str) -> bool:
        raise ParamErr("参数%s需要是文件." % key, )

    def throw_exts(self, key: str) -> bool:
        raise ParamErr("文件%s应该为类型%r." % (key, self.exts,))


class Request(JsonAble):
    def __init__(self, post: dict = None, ):
        if post is None:
            post = self.get_request()
        self.__data = post
        self.__meta: Dict[str, List[ValidateType]] = {}

    @classmethod
    def data_decode(cls, datad: bytes) -> str:
        try:
            rest = datad.decode("utf-8")
            return str(rest)
        except:
            rest = datad.decode("gbk")
            return str(rest)

    @classmethod
    def get_request(cls) -> dict:
        try:
            query = cls.get_query()
            post = _request.values.to_dict()
            if not post:
                try:
                    post = _request.get_json()
                except:
                    rest = _request.data
                    rest = cls.data_decode(rest)
                    if len(rest):
                        post = json.loads(rest)
                    else:
                        post = {}
            if not post:
                post = {}
            query.update(post)
            query.update(cls.getRequestFiles())
            return query
        except:
            log().trace()
            raise (ParamErr("请求内容无法解析:\n%r\n" % repr(_request.data)[:200]))

    @classmethod
    def get_query(cls, ) -> dict:
        return dict(_request.args)

    @classmethod
    def getRequestFiles(cls) -> Dict[str, List[FileStorage]]:
        try:
            files = ImmutableMultiDict(_request.files)
            rest = {}
            for k in files:
                tmp = files.getlist(k)
                for i, f in enumerate(tmp):
                    if isinstance(f, FileStorage):
                        tmp[i].filename = secure_filename(f.filename)
                rest[k] = tmp
            return rest
        except:
            raise (ParamErr("请求内容无法解析。"))

    def __repr__(self):
        return repr(self.__data)

    def keys(self) -> List[str]:
        res = list(self.__data.keys())
        return res

    def __getitem__(self, item):
        if item in self.__data.keys():
            return self.__data[item]
        return None

    def __setitem__(self, key, value):
        self.__data[key] = value

    def __delitem__(self, key):
        if key in self.__data.keys():
            del self.__data[key]

    def get_dict(self) -> dict:
        res = deepcopy(self.__data)
        return res

    @classmethod
    def _checkfile(cls, vali: dict) -> bool:
        for valis in vali.values():
            for vali in valis:
                if isinstance(vali, IsFile):
                    return True
        return False

    def has(self, key) -> bool:
        if key in self.__data.keys():
            return True
        return False

    def get(self, key: str, default: None):
        return self.param(key=key, default=default)

    def file(self, key: str):
        f: FileStorage = self.param(key)
        return f

    def param(self, key: Union[List[str], str] = None, type_class: ClassVar = None, default=None, all: bool = False):
        if all:
            return self.__data.copy()
        elif key is None:
            res = {}
            for key in self.__meta.keys():
                if self.has(key):
                    res[key] = self.param(key, default=default)
            return res
        elif isinstance(key, list):
            res = {}
            for keyt in key:
                res[keyt] = self.param(keyt, type_class=type_class, default=default, all=False)
            return res
        else:
            res = self.__data.get(key)
            if res is None:
                return default
            if type_class:
                res = type_class(res)
            return res

    def validate(self, validator: Dict[str, List[ValidateType]], ):
        obj = self.__data
        self.__meta = validator
        for key, valis in self.__meta.items():
            for vali in valis:
                vali.validate(obj, key)
        return self


def request(validater: Dict[str, List[ValidateType]] = None, reqdata: dict = None) -> Request:
    if validater is None:
        validater = {}
    res = Request(reqdata)
    res.validate(validater)
    return res


def request_data():
    return Request.get_request()
