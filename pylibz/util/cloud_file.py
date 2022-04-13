# -*- coding: utf-8 -*-

from .json_able import JsonAble
from ..func import datetime, etag_format, Path


class CloudFile(JsonAble):
    __empty_etag = "d41d8cd98f00b204e9800998ecf8427e"

    # __slots__ = ["etag", "key", "size", "versions", "s3_version_id", "last_time", "isDir", ]

    def __init__(self, key: str = None, size: int = 0, etag: str = __empty_etag, s3_version_id: str = None,
                 versions: list = None, last_time: datetime = None):
        if etag is not None:
            etag = etag_format(etag)
        self.key = key
        self.size = int(size)
        self.etag = etag
        if versions is None:
            versions = list()
        self.versions = versions
        self.s3_version_id = s3_version_id
        self.last_time = last_time
        self.isDir = False
        if self.size == 0 and etag == self.__empty_etag and (not key or key[-1] == "/"):
            self.isDir = True

    def get_name(self):
        return Path(self.key).name

    def get_suffix(self):
        p = Path(self.key)
        s = p.suffix.lower()
        return s.strip(".")

    def is_none(self):
        return self.key is None

    def __hash__(self):
        return self.key

    def __eq__(self, other):
        if isinstance(other, CloudFile) and self.etag == other.etag:
            return True
        return False

    @staticmethod
    def file_sort_time(a):
        return a.key
