# -*- coding: utf-8 -*-
import json
from copy import deepcopy
from datetime import datetime, timedelta
from multiprocessing import Process
from pathlib import Path
from string import Template
from time import sleep, time
from traceback import format_exc
from urllib.parse import quote_plus as url_quote, urlsplit, urlunsplit

url_quote = url_quote
urlsplit = urlsplit
urlunsplit = urlunsplit
Template = Template
time = time
sleep = sleep
Process = Process
json = json
format_exc = format_exc
Path = Path
datetime = datetime
timedelta = timedelta
deepcopy = deepcopy
