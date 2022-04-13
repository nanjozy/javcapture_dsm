# -*- coding: utf-8 -*-
from subprocess import getstatusoutput


def shell(command: str):
    status, output = getstatusoutput(command)
    return status, output
