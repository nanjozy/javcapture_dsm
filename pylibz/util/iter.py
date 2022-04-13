# -*- coding: utf-8 -*-
from multiprocessing import Process, Queue as get_Queue
from multiprocessing.queues import Queue
from typing import Callable, Iterator, List, Union


class IterMidWare:
    def __init__(self, itor: Iterator, action: Union[Callable, List[Callable]], reset: bool = True, ):
        self.itor = itor
        if not isinstance(action, list):
            action = [action]
        self.action: List[Callable] = action
        self.reset = reset

    def __iter__(self):
        if self.reset:
            self.itor = iter(self.itor)
        return self

    def __next__(self):
        res = self.itor.__next__()
        for action in self.action:
            res = action(res)
        return res


class MultiProcessIter:
    def __init__(self, queue: int = 10, ):
        self.queue = queue
        self.p: Process = None
        self.q: Queue = None

    def get_max_queue(self):
        return self.queue

    def __iter__(self):
        self.close()
        return self

    def close(self):
        if isinstance(self.p, Process):
            if self.p.is_alive():
                self.p.terminate()
        if isinstance(self.q, Queue):
            self.q.close()
        self.p = None
        self.q = None
        self.after_close()

    def start(self):
        self.close()
        self.q = get_Queue(maxsize=self.get_max_queue())
        self.p = self.main_process()
        self.before_start()
        self.p.start()

    def __next__(self):
        raw = self.next()
        if raw is not None:
            return raw
        else:
            raise StopIteration

    def next(self):
        if self.p is None or self.q is None:
            self.start()
        raw = self.q.get()
        if raw is not None:
            if isinstance(raw, Exception):
                self.close()
                self.when_end(error=raw)
                raise raw
            raw = self.when_next(raw)
            if raw is None:
                return self.next()
            # log().info(len(raw))
            return raw
        else:
            self.close()
            self.when_end(error=None)
            return None

    def after_close(self):
        pass

    def before_start(self):
        pass

    def when_next(self, raw):
        return raw

    def when_end(self, error: Exception = None):
        pass

    def main_process(self) -> Process:
        def p(q: Queue):
            q.put(None)
            return

        return Process(target=p, args=(self.q,))

class SQ:
    def __init__(self):
        self.queue=[]

class SingleProcessIter:
    def __init__(self, queue: int = 10, ):
        self.queue = queue
        self.p: Process = None
        self.q: Queue = None

    def get_max_queue(self):
        return self.queue

    def __iter__(self):
        self.close()
        return self

    def close(self):
        if isinstance(self.p, Process):
            if self.p.is_alive():
                self.p.terminate()
        if isinstance(self.q, Queue):
            self.q.close()
        self.p = None
        self.q = None
        self.after_close()

    def start(self):
        self.close()
        self.q = get_Queue(maxsize=self.get_max_queue())
        self.p = self.main_process()
        self.before_start()
        self.p.start()

    def __next__(self):
        raw = self.next()
        if raw is not None:
            return raw
        else:
            raise StopIteration

    def next(self):
        if self.p is None or self.q is None:
            self.start()
        raw = self.q.get()
        if raw is not None:
            if isinstance(raw, Exception):
                self.close()
                self.when_end(error=raw)
                raise raw
            raw = self.when_next(raw)
            if raw is None:
                return self.next()
            # log().info(len(raw))
            return raw
        else:
            self.close()
            self.when_end(error=None)
            return None

    def after_close(self):
        pass

    def before_start(self):
        pass

    def when_next(self, raw):
        return raw

    def when_end(self, error: Exception = None):
        pass

    def main_process(self) -> Process:
        def p(q: Queue):
            q.put(None)
            return

        return Process(target=p, args=(self.q,))
