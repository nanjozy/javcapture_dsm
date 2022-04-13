# -*- coding: utf-8 -*-
import logging
import sys


class StdHandler(logging.Handler):
    terminator = '\n'

    def __init__(self, err_level: int = logging.WARNING):
        super().__init__()
        self.err_level = err_level
        self.stdout = sys.stdout
        self.stderr = sys.stderr

    def flush(self, stream=None):
        self.acquire()
        try:
            if stream:
                if hasattr(stream, "flush"):
                    stream.flush()
            else:
                if self.stdout and hasattr(self.stdout, "flush"):
                    self.stdout.flush()
                if self.stderr and hasattr(self.stderr, "flush"):
                    self.stderr.flush()
        finally:
            self.release()

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            if record.levelno >= self.err_level:
                stream = self.stderr
            else:
                stream = self.stdout
            stream.write(msg + self.terminator)
            self.flush(stream)
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)

    def __repr__(self):
        return '<%s>' % self.__class__.__name__
