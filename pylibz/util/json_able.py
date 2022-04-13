# -*- coding: utf-8 -*-  
import inspect
import json
from pathlib import Path
from typing import ClassVar, Union
from copy import deepcopy


class JsonAble:
    __type__ = None
    _type_key = "__type"

    @classmethod
    def parser_cls(cls) -> list:
        return [cls]

    @classmethod
    def get_type(cls) -> str:
        if cls.__type__ is not None:
            return cls.__type__
        res = str(cls.__name__)
        return res

    @classmethod
    def get_init_params(cls) -> list:
        from ..func import function_params
        params = function_params(cls.__init__)
        return params

    @classmethod
    def filte_init_params(cls, params: dict) -> dict:
        param_list = cls.get_init_params()
        for key in list(params.keys()):
            if key not in param_list:
                del params[key]
        return params

    def list_type_check(self, nodes: list, type_cls: ClassVar) -> list:
        if nodes is not None:
            if not isinstance(nodes, list):
                nodes = [nodes, ]
            tmp = []
            for node in nodes:
                if node is not None:
                    tmp.append(node)
            nodes = tmp
            for node in nodes:
                assert isinstance(node, type_cls), "%s (type:%s)is not %s" % (node, type(node), type_cls,)
        else:
            nodes = []
        return nodes

    @classmethod
    def from_dict(cls, obj: Union[str, dict]):
        if isinstance(obj, str):
            obj = json.loads(obj)
        param_list = cls.get_init_params()
        params = {}
        for key, value in obj.items():
            if key == cls._type_key:
                continue
            if "kwargs" in param_list or key in param_list:
                params[key] = value
        return cls(**params)

    @classmethod
    def get_type_key(cls) -> str:
        return cls._type_key

    @classmethod
    def create_id(cls) -> str:
        from ..func import tuid
        return tuid()

    @classmethod
    def get_parser_cls(cls, li: list = None) -> list:
        if li is None:
            li = []
        for type_cls in cls.parser_cls():
            assert issubclass(type_cls, JsonAble)
            if type_cls not in li:
                li.append(type_cls)
                for tct in type_cls.get_parser_cls(li):
                    if tct not in li:
                        li.append(tct)
        return li

    @classmethod
    def parse(cls, obj):
        if isinstance(obj, dict):
            type_keys = set()
            type_dicts = dict()
            for type_cls in cls.get_parser_cls():
                assert issubclass(type_cls, JsonAble)
                type_keys.add(type_cls.get_type_key())
                type_dicts[type_cls.get_type()] = type_cls
            clst = None
            for tk in type_keys:
                if tk in obj.keys():
                    if obj[tk] in type_dicts.keys():
                        clst = type_dicts[obj[tk]]
                        break

            for key, value in obj.items():
                obj[key] = cls.parse(value)
            if clst is None:
                return obj
            else:
                return clst.from_dict(obj)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                obj[i] = cls.parse(v)
            return obj
        else:
            return obj

    @classmethod
    def obj_to_dict(cls, obj, for_tpl: bool = False, reverse_able: bool = True):
        if isinstance(obj, JsonAble):
            return obj.to_dict(for_tpl=for_tpl, reverse_able=reverse_able)
        elif isinstance(obj, list):
            tmp = []
            for valuet in obj:
                tmp.append(cls.obj_to_dict(valuet, for_tpl=for_tpl, reverse_able=reverse_able))
            return tmp
        elif isinstance(obj, dict):
            tmp = {}
            for keyt, valuet in obj.items():
                valuet = cls.obj_to_dict(valuet, for_tpl=for_tpl, reverse_able=reverse_able)
                tmp[keyt] = valuet
            return tmp
        else:
            return obj

    def to_dict(self, for_tpl: bool = False, reverse_able: bool = True) -> dict:
        obj = dict(vars(self))
        param_list = self.get_init_params()
        new = {}
        for key, value in obj.items():
            if key == "self":
                continue
            if reverse_able and key not in param_list:
                # if "kwargs" not in param_list:
                continue
            new[key] = self.obj_to_dict(value, for_tpl=for_tpl, reverse_able=reverse_able)
        obj = new
        if not for_tpl:
            obj[self.get_type_key()] = self.get_type()
        else:
            res = {}
            for key, value in obj.items():
                if key[0:1] == "_":
                    continue
                if isinstance(value, list):
                    pass
                elif isinstance(value, dict):
                    for keyt, valuet in value.items():
                        if keyt == key:
                            keyt = key
                        else:
                            keyt = "%s_%s" % (key, keyt,)
                        res[keyt] = valuet
                else:
                    res[key] = value
            obj = res
        return obj

    def __repr__(self):
        return "#%s\n%s" % (self.__class__.__name__, str(self))

    def __hash__(self):
        return hash(str(self))

    def __getattr__(self, name, ):
        if name[:4] == "get_" and len(name) > 4:
            attr = name[4:]
            if hasattr(self, attr):
                return lambda: deepcopy(getattr(self, attr))
        raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))

    def __str__(self):
        from ..func import jsondumps
        res = self.to_dict(reverse_able=False)
        res2 = self.to_dict(reverse_able=True)
        for k, v in res.items():
            if k not in res2.keys():
                res[k] = repr(v)
        return jsondumps(res, indent=4)

    def __eq__(self, other):
        return repr(self) == repr(other)

    @classmethod
    def __file__(cls):
        return Path(inspect.getfile(cls)).absolute().as_posix()

    @classmethod
    def __folder__(cls):
        return Path(cls.__file__()).parent.as_posix()
