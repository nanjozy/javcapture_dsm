# -*- coding: utf-8 -*-

import traceback
from concurrent.futures import Future, ThreadPoolExecutor
from threading import BoundedSemaphore, Thread as _thread
from typing import Callable, Dict

from ..func import cpu_count, sleep, tuid


class BoundedExecutor:
    """BoundedExecutor behaves as a ThreadPoolExecutor which will block on
    calls to submit() once the limit given as "bound" work items are queued for
    execution.
    :param bound: Integer - the maximum number of items in the work queue
    :param max_workers: Integer - the size of the thread pool
    """

    def __init__(self, bound: int, max_workers: int = None):
        if max_workers is None:
            max_workers = cpu_count()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = BoundedSemaphore(bound + max_workers)

    """See concurrent.futures.Executor#submit"""

    def submit(self, fn, *args, **kwargs) -> Future:
        self.semaphore.acquire()
        try:
            future = self.executor.submit(fn, *args, **kwargs)
        except:
            self.semaphore.release()
            raise
        else:
            future.add_done_callback(lambda x: self.semaphore.release())
            return future

    """See concurrent.futures.Executor#shutdown"""

    def shutdown(self, wait=True):
        self.executor.shutdown(wait)


__pool = None


def thread(func: Callable, *args, **kwargs):
    global __pool
    if __pool is None:
        max_worker = cpu_count()
        __pool = BoundedExecutor(max_worker * 2, max_workers=max_worker)
    th = __pool.submit(func, *args, **kwargs)
    return th


class Thread(_thread):
    def __init__(self, action: Callable, *args, daemon: bool = None, **kwargs):
        super().__init__(daemon=daemon)
        self.action = action
        self.args = args
        self.kwargs = kwargs
        self.results = None
        self.error = None
        self.traceback = None

    def run(self):
        try:
            self.results = self.action(*self.args, **self.kwargs)
            return self.results
        except Exception as e:
            self.error = e
            self.traceback = traceback.format_exc()

    def result(self, timeout: int = None):
        self.join(timeout=timeout)
        if self.error is not None:
            raise self.error
        return self.result


class Pool:
    def __init__(self, size: int, refresh_wait: float = 0.1):
        self.__closed = False
        self.size = size
        self.__ths: Dict[str, Thread] = {}
        self.__refresh_wait = refresh_wait
        self.__c_th = Thread(self.__check_ths, daemon=True)
        self.__c_th.start()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is None:
            pass
        else:
            return None

    def __check_ths(self):
        while True:
            for key in list(self.__ths.keys()):
                if not self.__ths[key].is_alive():
                    del self.__ths[key]
            if self.__closed:
                break
            sleep(self.__refresh_wait)
        del self

    def __get_tmp_id(self) -> str:
        while True:
            id = tuid()
            if id not in self.__ths.keys():
                return id

    def submit(self, action: Callable, *args, **kwargs):
        self.raise_on_close()
        while True:
            if len(self.__ths) < self.size:
                break
            sleep(self.__refresh_wait)
        th = Thread(action, *args, **kwargs)
        th.start()
        self.__ths[self.__get_tmp_id()] = th
        return th

    def raise_on_close(self):
        assert self.__closed == False

    def join(self):
        self.raise_on_close()
        while True:
            # print("k", len(self.__ths))
            if len(self.__ths) < 1:
                # print("end")
                return True
            sleep(self.__refresh_wait)

    def close(self):
        self.__closed = True
