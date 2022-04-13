# -*- coding: utf-8 -*-
import logging
import os
from pathlib import Path

from ..func import ensure_folder, get_now

try:
    import codecs
except ImportError:
    codecs = None


class FileHandler(logging.FileHandler):

    def __init__(self, filename, encoding: str = "utf-8", delay: bool = True):
        if "{date}" not in filename:
            filename = Path(filename).with_suffix(".{date}" + Path(filename).suffix).as_posix()
        self.prefix = filename

        # 日志文件日期后缀
        self.suffix = "%Y-%m-%d"
        # self.suffix_re = r"\d{4}-\d{2}-\d{2}-\d{2}"

        self.date_suffix = get_now().strftime(self.suffix)
        self.atime = None
        # self.reg = re.compile(self.prefix.format(date=self.suffix_re, ))
        self.filePath = self.prefix.format(date=self.date_suffix, )
        # 获得文件夹路径
        __dir = Path(self.filePath).parent.as_posix()
        try:
            ensure_folder(__dir)
        except Exception:
            print("创建文件夹失败: " + self.filePath)
            pass
        self.filePath, self.date_suffix = self.get_file_path()

        if codecs is None:
            encoding = None

        logging.FileHandler.__init__(self, self.filePath, 'a+', encoding, delay)

    def get_atime(self):
        if os.path.exists(self.filePath):
            return os.path.getatime(self.filePath)
        return None

    def _open(self):
        f = super()._open()
        self.atime = self.get_atime()
        return f

    def get_file_path(self):
        date_suffix = get_now().strftime(self.suffix)
        path = self.prefix.format(date=date_suffix, )
        if path != self.filePath:
            # 获得文件夹路径
            __dir = Path(path).parent.as_posix()
            try:
                ensure_folder(__dir)
            except Exception:
                print("创建文件夹失败: " + __dir)
                pass
        return path, date_suffix

    def shouldChangeFileToWrite(self):
        __filePath, date_suffix = self.get_file_path()
        if __filePath != self.filePath:
            self.filePath = __filePath
            self.date_suffix = date_suffix
            return True
        return False

    def doChangeFile(self):
        self.baseFilename = Path(self.filePath).absolute().as_posix()
        if self.stream:
            self.stream.close()
            self.stream = None
        if not self.delay:
            self.stream = self._open()

    def emit(self, record):
        try:
            if self.shouldChangeFileToWrite():
                self.doChangeFile()
            if self.atime != self.get_atime() or not os.path.exists(self.filePath):
                if self.stream:
                    self.stream.close()
                self.stream = None
                if not self.delay:
                    self.stream = self._open()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
        super().emit(record)
