# -*- coding: utf-8 -*-
import json
from _io import TextIOWrapper
from pathlib import Path
from typing import Union


class JsonWriter:
    def __init__(self, file: Union[str, Path, TextIOWrapper]):
        if isinstance(file, Path):
            path = file.as_posix()
            self.path = path
            self.file: TextIOWrapper = None
        elif isinstance(file, str):
            self.path = file
            self.file: TextIOWrapper = None
        else:
            self.path = None
            self.file: TextIOWrapper = file

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.file is not None:
            self.file.close()

    def writerow(self, row):
        if self.file is None:
            self.file = open(self.path, mode="w+", encoding="utf-8")
        t = json.dumps(row, ensure_ascii=False)
        self.file.write(t)
        self.file.write("\n")

    def writerows(self, rows: list):
        for row in rows:
            self.writerow(row)


class JsonReader:
    def __init__(self, file: Union[str, Path, TextIOWrapper]):
        if isinstance(file, Path):
            path = file.as_posix()
            self.path = path
            self.file: TextIOWrapper = None
        elif isinstance(file, str):
            self.path = file
            self.file: TextIOWrapper = None
        else:
            self.path = None
            self.file: TextIOWrapper = file

    def __enter__(self):
        return iter(self)

    def __iter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        if self.file is not None:
            self.file.close()

    def next(self):
        if self.file is None:
            self.file = open(self.path, mode="w+", encoding="utf-8")
        line = self.file.readline()
        if not line:
            return None
        t = json.loads(line)
        return t

    def __next__(self):
        next = self.next()
        if next is None:
            raise StopIteration()
        return next
