# -*- coding: utf-8 -*-
import logging
import os
import re
from pathlib import Path

from ..func import du, ensure_folder, get_now, get_size

try:
    import codecs
except ImportError:
    codecs = None


class MultiprocessHandler(logging.FileHandler):
    """支持多进程的TimedRotatingFileHandler"""

    def __init__(self, filename, when='D', backupCount: int = 0, encoding: str = "utf-8", delay: bool = True,
                 chunksize: int = 10 * 1024 * 1024):
        """filename 日志文件名,when 时间间隔的单位,backupCount 保留文件个数
        delay 是否开启 OutSteam缓存
            True 表示开启缓存，OutStream输出到缓存，待缓存区满后，刷新缓存区，并输出缓存数据到文件。
            False表示不缓存，OutStrea直接输出到文件"""
        if "{date}" not in filename:
            filename = filename + ".{date}"
        if "{num}" not in filename:
            filename = filename + ".{num}"
        self.prefix = filename
        self.backupCount = backupCount
        self.when = when.upper()
        self.chunksize = chunksize
        # 正则匹配 年-月-日
        self.extMath = r"^\d{4}-\d{2}-\d{2}"

        # S 每秒建立一个新文件
        # M 每分钟建立一个新文件
        # H 每天建立一个新文件
        # D 每天建立一个新文件
        when_dict = {
            'S': "%Y-%m-%d-%H-%M-%S",
            'M': "%Y-%m-%d-%H-%M",
            'H': "%Y-%m-%d-%H",
            'D': "%Y-%m-%d"
        }
        when_re_dict = {
            'S': r"\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}",
            'M': r"\d{4}-\d{2}-\d{2}-\d{2}-\d{2}",
            'H': r"\d{4}-\d{2}-\d{2}-\d{2}",
            'D': r"\d{4}-\d{2}-\d{2}"
        }
        # 日志文件日期后缀
        self.suffix = when_dict.get(when)
        self.suffix_re = when_re_dict.get(when)
        if not self.suffix:
            raise ValueError(u"指定的日期间隔单位无效: %s" % self.when)
        self.date_suffix = get_now().strftime(self.suffix)

        self.date_count_fmt = "%02d"
        self.date_count_re = r"(\d+)"
        # 使用当前时间，格式化文件格式化字符串
        self.date_count = self.get_start_count(self.date_suffix)

        self.reg = re.compile(self.prefix.format(date=self.suffix_re, num=self.date_count_re))
        self.filePath = self.prefix.format(date=self.date_suffix, num=self.date_count_fmt % self.date_count)
        # 获得文件夹路径
        __dir = Path(self.filePath).parent.as_posix()
        try:
            ensure_folder(__dir)
        except Exception:
            print(u"创建文件夹失败")
            print(u"文件夹路径：" + self.filePath)
            pass
        self.filePath, self.date_count, self.date_suffix = self.get_file_path()
        if codecs is None:
            encoding = None

        logging.FileHandler.__init__(self, self.filePath, 'a+', encoding, delay)

    def get_start_count(self, date_suffix: str):
        res = 0
        f = Path(self.prefix.format(date=date_suffix, num=res)).parent.as_posix()
        reg = re.compile(self.prefix.format(date=date_suffix, num=self.date_count_re))
        for file in du(f, file_only=True):
            t = reg.findall(file.absolute().as_posix())
            if len(t):
                tt = int(t.pop())
                if tt > res:
                    res = tt
        return res

    def get_num(self, path: str, date_suffix: str = None):
        if date_suffix is None:
            date_suffix = self.date_suffix
        reg = re.compile(self.prefix.format(date=date_suffix, num=self.date_count_re))
        t = reg.findall(path)
        if len(t):
            tt = int(t.pop())
            return tt
        return -1

    def find_next(self, start: int, date: str):
        num = start
        while True:
            path = self.prefix.format(date=date, num=self.date_count_fmt % num)
            size = get_size(path)
            if size and size >= self.chunksize:
                num += 1
            else:
                return num

    def get_file_path(self):
        date_suffix = get_now().strftime(self.suffix)
        if self.date_suffix == date_suffix:
            date_count = self.date_count
        else:
            date_count = self.get_start_count(date_suffix)
        date_count = self.find_next(date_count, date_suffix)
        path = self.prefix.format(date=date_suffix, num=self.date_count_fmt % date_count)
        if path != self.filePath:
            # 获得文件夹路径
            __dir = Path(path).parent.as_posix()
            try:
                ensure_folder(__dir)
            except Exception:
                print(u"创建文件夹失败")
                print(u"文件夹路径：" + path)
                pass
        return path, date_count, date_suffix

    def shouldChangeFileToWrite(self):
        """更改日志写入目的写入文件
        :return True 表示已更改，False 表示未更改"""
        # 以当前时间获得新日志文件路径
        __filePath, date_count, date_suffix = self.get_file_path()
        # 新日志文件日期 不等于 旧日志文件日期，则表示 已经到了日志切分的时候
        #   更换日志写入目的为新日志文件。
        # 例如 按 天 （D）来切分日志
        #   当前新日志日期等于旧日志日期，则表示在同一天内，还不到日志切分的时候
        #   当前新日志日期不等于旧日志日期，则表示不在
        # 同一天内，进行日志切分，将日志内容写入新日志内。
        if __filePath != self.filePath:
            self.filePath = __filePath
            self.date_count = date_count
            self.date_suffix = date_suffix
            return True
        return False

    def doChangeFile(self):
        """输出信息到日志文件，并删除多于保留个数的所有日志文件"""
        # 日志文件的绝对路径
        self.baseFilename = Path(self.filePath).absolute().as_posix()
        # stream == OutStream
        # stream is not None 表示 OutStream中还有未输出完的缓存数据
        if self.stream:
            # flush close 都会刷新缓冲区，flush不会关闭stream，close则关闭stream
            # self.stream.flush()
            self.stream.close()
            # 关闭stream后必须重新设置stream为None，否则会造成对已关闭文件进行IO操作。
            self.stream = None
        # delay 为False 表示 不OutStream不缓存数据 直接输出
        #   所有，只需要关闭OutStream即可
        if not self.delay:
            # 这个地方如果关闭colse那么就会造成进程往已关闭的文件中写数据，从而造成IO错误
            # delay == False 表示的就是 不缓存直接写入磁盘
            # 我们需要重新在打开一次stream
            # self.stream.close()
            self.stream = self._open()
        # 删除多于保留个数的所有日志文件
        if self.backupCount > 0:
            # print('删除日志')
            for s in self.getFilesToDelete():
                # print(s)
                os.remove(s)

    def getFilesToDelete(self):
        """获得过期需要删除的日志文件"""
        dirName = Path(self.baseFilename).parent.as_posix()
        fileNames = du(dirName, file_only=True)
        result = []

        for fileName in fileNames:
            fileName = fileName.absolute().as_posix()
            if self.reg.match(fileName):
                result.append(fileName)
        result.sort(key=self.get_num, reverse=True)
        result = result[self.backupCount:]
        return result

    def emit(self, record):
        """发送一个日志记录
        覆盖FileHandler中的emit方法，logging会自动调用此方法"""
        try:
            if self.shouldChangeFileToWrite():
                self.doChangeFile()
            logging.FileHandler.emit(self, record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)
