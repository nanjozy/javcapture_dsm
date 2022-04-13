# -*- coding: utf-8 -*-  
import _thread
from typing import Callable, Dict

from ..func import cpu_count, get_now, kill, Process, sleep, time, tuid
from ..logging import log


class TimeProcess(Process):
    def __init__(self, group=None, target=None, name=None, args=None, kwargs=None, daemon=None, *_args, **_kwargs):
        self.start_time = None
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        super().__init__(group=group, target=target, name=name, args=args, kwargs=kwargs, daemon=daemon, *_args,
                         **_kwargs)

    def start(self) -> None:
        self.start_time = get_now()
        super().start()

    def get_start_time(self):
        if self.start_time is None:
            return get_now()
        return self.start_time


class Pool:
    def __init__(self, name: str, size: int = None):
        self.name = name
        if size is None:
            size = cpu_count()
        self.size = size
        self.pool: Dict[str, TimeProcess] = {}
        self.wait_queue = []
        _thread.start_new_thread(self.__refresh_queue, (), )
        self.closed = False

    def __hash__(self):
        return hash("ProcessPool@%s" % self.name)

    def close(self):
        self.wait_queue = []
        self.closed = True
        for p in self.pool.values():
            try:
                p.terminate()
            except:
                log().trace()

    def get_usable(self):
        return self.size - len(self.pool) - len(self.wait_queue)

    def __refresh_queue(self):
        while not self.closed:
            self.__check_pool()
            if len(self.pool) < self.size and len(self.wait_queue):
                while len(self.pool) < self.size and len(self.wait_queue):
                    name, process = self.wait_queue.pop(0)
                    process.start()
                    self.pool[name] = process
            else:
                sleep(0.5)

    def __check_pool(self):
        for name, process in list(self.pool.items()):
            if not process or not process.is_alive():
                self.__unregister_process(name)

    @classmethod
    def get_name(cls) -> str:
        return tuid()

    def get_pid(self, name: str) -> int:
        if name in self.pool.keys() and isinstance(self.pool[name], TimeProcess):
            return self.pool[name].pid

    def get_process_ids(self) -> list:
        return list(self.pool.keys())

    def __unregister_process(self, name: str):
        if name in self.pool.keys():
            del self.pool[name]

    def stop_process(self, name: str) -> bool:
        try:
            process: TimeProcess = self.pool.get(name)
            if process is None:
                return True
            if isinstance(process, TimeProcess):
                process.terminate()
                start_time = time()
                while process.is_alive():
                    sleep(0.1)
                    if time() - start_time > 30:
                        t = kill(process.pid, safe=True)
                        if t:
                            break
                        else:
                            return False
            self.__unregister_process(name)
            return True
        except:
            log().trace()
            return False

    def waste(self, name: str) -> bool:
        try:
            self.__unregister_process(name)
            return True
        except:
            log().trace()
            return False

    def __callback(self, name: str, process: TimeProcess, cb_args: tuple, cb_kwargs: dict, callback: Callable):
        process.join()
        if callback is not None:
            callback(*cb_args, **cb_kwargs)
        self.__unregister_process(name)

    def __wait_pool(self, name: str, process: TimeProcess):
        self.wait_queue.append((name, process))
        while True:
            flag = True
            for n, p in self.wait_queue:
                if n == name:
                    flag = False
                    break
            if flag:
                if name in self.pool.keys():
                    return True
            sleep(0.5)

    def submit(self, target: Callable = None, name: str = None, args: tuple = None, kwargs: dict = None, daemon=None,
               callback: Callable = None, cb_args: tuple = None, cb_kwargs: dict = None, ):
        assert target is not None
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        if cb_args is None:
            cb_args = ()
        if cb_kwargs is None:
            cb_kwargs = {}
        if name is None:
            name = self.get_name()
        process = TimeProcess(target=target, name=name, args=args, kwargs=kwargs, daemon=daemon, )
        self.__wait_pool(name, process)
        # try:
        #     process.start()
        # except AssertionError as e:
        #     if 'cannot start a process twice' in e.args:
        #         pass
        #     else:
        #         raise e
        _thread.start_new_thread(self.__callback, (),
                                 dict(name=name, process=process, cb_args=cb_args, cb_kwargs=cb_kwargs,
                                      callback=callback))
        return process, name


pool_instances = set()


def close_pool(name: str):
    global pool_instances
    try:
        pool = find_pool(name)
        if isinstance(pool, Pool):
            pool_instances.remove(pool)
            pool.close()
    except:
        log().trace()


def find_pool(name: str):
    global pool_instances
    for p in list(pool_instances):
        if isinstance(p, Pool):
            if p.name == name:
                return p
        else:
            pool_instances.remove(p)
    return None


def add_pool(name: str, size: int):
    from ..setting import on_windows

    if on_windows():
        from multiprocessing import freeze_support
        log().track("freeze_support")
        freeze_support()
    if size is None:
        from ..setting import config
        size = config("process").get("pool_size")
    try:
        pool_instances.add(Pool(name=name, size=size))
    except:
        log().trace()


def get_pool(size: int = None, name="default") -> Pool:
    pool = find_pool(name)
    if pool is not None:
        return pool
    add_pool(name, size)
    pool = find_pool(name)
    assert isinstance(pool, Pool)
    return pool


def get_process_config(pool_size: int = 8):
    from ..setting import Row
    return {
        "process": {
            "pool_size": Row(default=pool_size, cfg_type=int),
        }
    }
