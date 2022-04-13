# -*- coding: utf-8 -*-  
import csv
import io
from typing import List, Union
from uuid import UUID

from ..func import Path


class CsvProxyBase:
    NONE_CSV = '\vNone\v'
    TRUE_CSV = '\vTrue\v'
    FALSE_CSV = '\vFalse\v'
    QUOTE_NONNUMERIC = csv.QUOTE_NONNUMERIC
    QUOTE_ALL = csv.QUOTE_ALL
    QUOTE_NONE = csv.QUOTE_NONE
    QUOTE_MINIMAL = csv.QUOTE_MINIMAL

    @classmethod
    def get_none(cls, null_char: str, quoting: int, quotechar: str) -> (str, str):
        if quoting == csv.QUOTE_ALL or quoting == csv.QUOTE_NONNUMERIC:
            none_str = "%s%s%s" % (quotechar, null_char, quotechar)
            return none_str, cls.NONE_CSV
        else:
            return null_char, ''

    @classmethod
    def get_true(cls, quoting: int, quotechar: str) -> (str, str):
        if quoting == csv.QUOTE_ALL or quoting == csv.QUOTE_NONNUMERIC:
            none_str = "%s%s%s" % (quotechar, cls.TRUE_CSV, quotechar)
            if quoting == csv.QUOTE_ALL:
                n_str = "%sTrue%s" % (quotechar, quotechar)
            else:
                n_str = "True"
            return none_str, n_str
        else:
            return cls.TRUE_CSV, "True"

    @classmethod
    def get_false(cls, quoting: int, quotechar: str) -> (str, str):
        if quoting == csv.QUOTE_ALL or quoting == csv.QUOTE_NONNUMERIC:
            none_str = "%s%s%s" % (quotechar, cls.FALSE_CSV, quotechar)
            if quoting == csv.QUOTE_ALL:
                n_str = "%sFalse%s" % (quotechar, quotechar)
            else:
                n_str = "False"
            return none_str, n_str
        else:
            return cls.FALSE_CSV, "False"


class DictWriter(CsvProxyBase):
    def __init__(self, csvfile, header, null_char: str = None, *args, **kwargs):
        self.null_char = null_char
        self.writer = csv.DictWriter(csvfile, header, *args, **kwargs)

    def writeheader(self):
        self.writer.writeheader()

    def writerow(self, row: dict):
        row = row.copy()
        if self.null_char is not None:
            for key, value in row.items():
                if value is None:
                    row[key] = self.null_char
                elif value is True:
                    row[key] = self.TRUE_CSV
                elif value is False:
                    row[key] = self.FALSE_CSV
        for i, v in enumerate(row):
            if isinstance(v, UUID):
                row[i] = str(v)
        self.writer.writerow(row)

    def writerows(self, rows: List[dict]):
        for row in rows:
            self.writerow(row)


class DictWriter2:
    QUOTE_NONNUMERIC = csv.QUOTE_NONNUMERIC
    QUOTE_ALL = csv.QUOTE_ALL
    QUOTE_NONE = csv.QUOTE_NONE
    QUOTE_MINIMAL = csv.QUOTE_MINIMAL

    def __init__(self, csvfile, header, null_char: str = "", encoding="utf-8", quoting: int = csv.QUOTE_NONNUMERIC,
                 quotechar: str = "\"", *args, **kwargs):
        from ..func import suid
        self.null_char = null_char
        self.header = header
        self.quoting = quoting
        self.quotechar = quotechar
        self.args = args
        self.kwargs = kwargs
        self.null_tmp = "$%s&" % suid(3)
        # self.true_tmp = "#%s@" % suid(5)
        # self.false_tmp = "@%s#" % suid(4)
        self.nullt: str = None
        # self.truet: str = None
        # self.falset: str = None
        if isinstance(csvfile, (Path, str)):
            self.f = open(csvfile, mode="w+", encoding=encoding)
        else:
            self.f = csvfile

    def writeheader(self):
        c = csv.DictWriter(self.f, self.header, quoting=self.quoting, quotechar=self.quotechar, *self.args,
                           **self.kwargs)
        c.writeheader()

    def get_row(self, row: dict):
        tmp = row.copy()
        for h in self.header:
            if h not in tmp.keys():
                tmp[h] = None
        for k, v in tmp.items():
            if v is None:
                tmp[k] = self.null_tmp
            # elif v is False:
            #     tmp[k] = self.false_tmp
            # elif v is True:
            #     tmp[k] = self.true_tmp
            elif isinstance(v, UUID):
                tmp[k] = str(v)
        with io.StringIO() as f:
            c = csv.DictWriter(f, self.header, quoting=self.quoting, quotechar=self.quotechar, *self.args,
                               **self.kwargs)
            c.writerow(tmp)
            f.seek(0)
            t = f.read()
            t = t.replace(self.csv_none_char(), self.null_char)
            # if self.quoting == csv.QUOTE_ALL:
            #     false_str = "%sFalse%s" % (self.quotechar, self.quotechar)
            #     true_str = "%sTrue%s" % (self.quotechar, self.quotechar)
            #     t = t.replace(self.csv_false_char(), false_str)
            #     t = t.replace(self.csv_true_char(), true_str)
            # else:
            #     t = t.replace(self.csv_false_char(), "False")
            #     t = t.replace(self.csv_true_char(), "True")
            return t

    def csv_none_char(self):
        if self.nullt is None:
            if self.quoting in (csv.QUOTE_ALL, csv.QUOTE_NONNUMERIC):
                none_str = "%s%s%s" % (self.quotechar, self.null_tmp, self.quotechar)
                self.nullt = none_str
            else:
                self.nullt = self.null_tmp
        return self.nullt

    # def csv_false_char(self):
    #     if self.falset is None:
    #         if self.quoting in (csv.QUOTE_ALL, csv.QUOTE_NONNUMERIC):
    #             false_str = "%s%s%s" % (self.quotechar, self.false_tmp, self.quotechar)
    #             self.falset = false_str
    #         else:
    #             self.falset = self.false_tmp
    #     return self.falset
    #
    # def csv_true_char(self):
    #     if self.truet is None:
    #         if self.quoting in (csv.QUOTE_ALL, csv.QUOTE_NONNUMERIC):
    #             true_str = "%s%s%s" % (self.quotechar, self.true_tmp, self.quotechar)
    #             self.truet = true_str
    #         else:
    #             self.truet = self.true_tmp
    #     return self.truet

    def writerow(self, row: dict):
        self.f.write(self.get_row(row))

    def writerows(self, rows: List[dict]):
        for row in rows:
            self.writerow(row)


class Writer2:
    QUOTE_NONNUMERIC = csv.QUOTE_NONNUMERIC
    QUOTE_ALL = csv.QUOTE_ALL
    QUOTE_NONE = csv.QUOTE_NONE
    QUOTE_MINIMAL = csv.QUOTE_MINIMAL

    def __init__(self, csvfile, null_char: str = "", encoding="utf-8", quoting: int = csv.QUOTE_NONNUMERIC,
                 quotechar: str = "\"", *args, **kwargs):
        from ..func import suid
        self.null_char = null_char
        self.quoting = quoting
        self.quotechar = quotechar
        self.args = args
        self.kwargs = kwargs
        self.null_tmp = "\v%s\v" % suid(3)
        # self.true_tmp = "\v%s\v" % suid(5)
        # self.false_tmp = "\v%s\v" % suid(4)
        self.nullt: str = None
        # self.truet: str = None
        # self.falset: str = None
        if isinstance(csvfile, (Path, str)):
            self.f = open(csvfile, mode="w+", encoding=encoding)
        else:
            self.f = csvfile

    def get_row(self, row):
        tmp = row.copy()
        for i, v in enumerate(tmp):
            if v is None:
                tmp[i] = self.null_tmp
            # elif v is False:
            #     tmp[i] = self.false_tmp
            # elif v is True:
            #     tmp[i] = self.true_tmp
            elif isinstance(v, UUID):
                tmp[i] = str(v)
        with io.StringIO() as f:
            c = csv.writer(f, quoting=self.quoting, quotechar=self.quotechar, *self.args, **self.kwargs)
            c.writerow(tmp)
            f.seek(0)
            t = f.read()
            t = t.replace(self.csv_none_char(), self.null_char)
            # if self.quoting == csv.QUOTE_ALL:
            #     false_str = "%sFalse%s" % (self.quotechar, self.quotechar)
            #     true_str = "%sTrue%s" % (self.quotechar, self.quotechar)
            #     t = t.replace(self.csv_false_char(), false_str)
            #     t = t.replace(self.csv_true_char(), true_str)
            # else:
            #     t = t.replace(self.csv_false_char(), "False")
            #     t = t.replace(self.csv_true_char(), "True")
            return t

    def csv_none_char(self):
        if self.nullt is None:
            if self.quoting in (csv.QUOTE_ALL, csv.QUOTE_NONNUMERIC):
                none_str = "%s%s%s" % (self.quotechar, self.null_tmp, self.quotechar)
                self.nullt = none_str
            else:
                self.nullt = self.null_tmp
        return self.nullt

    # def csv_false_char(self):
    #     if self.falset is None:
    #         if self.quoting in (csv.QUOTE_ALL, csv.QUOTE_NONNUMERIC):
    #             false_str = "%s%s%s" % (self.quotechar, self.false_tmp, self.quotechar)
    #             self.falset = false_str
    #         else:
    #             self.falset = self.false_tmp
    #     return self.falset
    #
    # def csv_true_char(self):
    #     if self.truet is None:
    #         if self.quoting in (csv.QUOTE_ALL, csv.QUOTE_NONNUMERIC):
    #             true_str = "%s%s%s" % (self.quotechar, self.true_tmp, self.quotechar)
    #             self.truet = true_str
    #         else:
    #             self.truet = self.true_tmp
    #     return self.truet

    def writerow(self, row: list):
        self.f.write(self.get_row(row))

    def writerows(self, rows: List[Union[list, tuple]]):
        for row in rows:
            self.writerow(row)


class Writer(CsvProxyBase):
    def __init__(self, csvfile, null_char: str = None, escapechar: str = None, *args, **kwargs):
        if null_char is None:
            null_char = CsvProxyBase.NONE_CSV
        self.null_char = null_char
        self.escapechar = escapechar
        self.writer = csv.writer(csvfile, escapechar=escapechar, *args, **kwargs)

    def writerow(self, row: list):
        for i, v in enumerate(row):
            # if self.escapechar == "\\" and isinstance(v, str):
            #     row[i] = v.replace("\\", "\\\\")
            if v is None:
                row[i] = self.null_char
            elif v is True:
                row[i] = self.TRUE_CSV
            elif v is False:
                row[i] = self.FALSE_CSV
            elif isinstance(v, UUID):
                row[i] = str(v)
        self.writer.writerow(row)

    def writerows(self, rows: List[Union[list, tuple]]):
        for row in rows:
            self.writerow(row)


class Reader(CsvProxyBase):
    def __init__(self, csvfile, null_chars: list = None, none_values: list = None, *args, **kwargs):
        if null_chars is None and none_values is None:
            null_chars = ["<None>", "null", ""]
        if null_chars is None:
            null_chars = []
        if none_values is None:
            none_values = []
        if isinstance(null_chars, str):
            null_chars = [null_chars]
        if isinstance(none_values, str):
            none_values = [none_values]
        null_chars = list(set(none_values + null_chars))
        self.null_chars = null_chars
        self.reader = csv.reader(csvfile, *args, **kwargs)

    def __iter__(self):
        return self

    def __next__(self) -> list:
        row = self.next()
        if row is None:
            raise StopIteration()
        return row

    def next(self):
        try:
            row = self.reader.__next__()
            if isinstance(row, (list, tuple)):
                row = list(row)
                for i, v in enumerate(row):
                    if v in self.null_chars:
                        row[i] = None
                    elif v == self.TRUE_CSV:
                        row[i] = True
                    elif v == self.FALSE_CSV:
                        row[i] = False
                    elif isinstance(v, float) and int(v) == v:
                        row[i] = int(v)
            return row
        except StopIteration:
            return None


class DictReader(CsvProxyBase):
    def __init__(self, csvfile, null_chars: list = None, none_values: list = None, *args, **kwargs):
        if null_chars is None:
            null_chars = none_values
        if isinstance(null_chars, str):
            null_chars = [null_chars]
        if null_chars is None:
            null_chars = ["<None>", "null", ""]
        self.null_chars = null_chars
        self.reader = csv.reader(csvfile, *args, **kwargs)

        self.__header: list = None

    def __iter__(self):
        return self

    def __next__(self) -> dict:
        row = self.next()
        return row

    def next(self):
        row = self.reader.__next__()
        if isinstance(row, tuple):
            row = list(row)
        if isinstance(row, list):
            for i, v in enumerate(row):
                if v in self.null_chars:
                    row[i] = None
                elif v == self.TRUE_CSV:
                    row[i] = True
                elif v == self.FALSE_CSV:
                    row[i] = False
                elif isinstance(v, float) and int(v) == v:
                    row[i] = int(v)
        if self.__header is None:
            self.__header = row
            return self.next()
        else:
            d = {}
            for i, v in enumerate(row):
                if i < len(self.__header):
                    d[self.__header[i]] = v
                else:
                    d["__extend_field_%s" % i] = v
            return d


def list_to_csv(datas: List[list],
                null_char: str = "<None>",
                quoting: int = csv.QUOTE_ALL,
                quotechar: str = "\"",
                *args, **kwargs) -> str:
    with io.StringIO() as f:
        Writer(f, *args, null_char=null_char, quoting=quoting, quotechar=quotechar, **kwargs).writerows(datas)
        f.seek(0)
        res = f.read()
    none_str, new_none = CsvProxyBase.get_none(null_char=null_char, quoting=quoting, quotechar=quotechar)
    res = res.replace(none_str, new_none)
    return res
