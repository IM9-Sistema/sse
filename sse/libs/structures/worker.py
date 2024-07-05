import asyncio
from collections.abc import Callable, Iterable, Mapping
from threading import Thread
from typing import Any
import logging
from abc import abstractclassmethod, ABCMeta
import inspect


class Worker(Thread):
    def __init__(self) -> None:
        super().__init__(None, self.run, daemon=True)
        self.logger = logging.getLogger("uvicorn")

    def run(self):
        self.logger.debug(f"Starting worker {self.__class__.__name__}")
        if inspect.iscoroutinefunction(self.work):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.work())
            loop.close()
        else:
            self.work()

    @classmethod
    def begin(cls):
        instance = cls()
        instance.start()
        return instance

    def work(self) -> None:
        pass

