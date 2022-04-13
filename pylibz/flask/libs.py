# -*- coding: utf-8 -*-
from flask import Blueprint, make_response, redirect
from werkzeug.datastructures import FileStorage

from ..func import in_uwsgi

in_uwsgi = in_uwsgi
FileStorage = FileStorage
Blueprint = Blueprint
redirect = redirect
make_response = make_response
