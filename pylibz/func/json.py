# -*- coding: utf-8 -*-
import json
from copy import deepcopy


def jsonify(obj) -> str:
    from ..util import JSONEncoder
    return JSONEncoder().encode(obj)


def jsondumps(obj, indent: int = 4, ) -> str:
    from ..util import jsonPreformat
    objt = deepcopy(obj)
    objt = jsonPreformat(objt)
    return json.dumps(objt, ensure_ascii=False, indent=indent, )


def print_json(obj, indent: int = 4, ) -> str:
    print(jsondumps(obj, indent=indent, ))
