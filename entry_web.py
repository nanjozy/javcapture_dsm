#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from javapi import Main

cfg = Main(name=__name__, log_name="web", file=__file__, env=Main.DEV,
           log_level=Main.WARNING, no_log=True, log_recycle=False, cfg_master=True)
app = cfg.flask_app()
