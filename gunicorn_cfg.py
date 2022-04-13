# config.py
import gevent.monkey

gevent.monkey.patch_all()

loglevel = 'info'
bind = "0.0.0.0:5004"
daemon = False

# 启动的进程数
workers = 2
worker_class = 'gevent'
x_forwarded_for_header = 'X-FORWARDED-FOR'
