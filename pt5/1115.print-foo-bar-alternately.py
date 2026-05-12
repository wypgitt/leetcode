from __future__ import annotations

from threading import Semaphore
from typing import Callable


class FooBar:
    def __init__(self, n):
        self.n = n
        self.foo_turn = Semaphore(1)
        self.bar_turn = Semaphore(0)

    def foo(self, printFoo: Callable[[], None]) -> None:
        for _ in range(self.n):
            self.foo_turn.acquire()
            printFoo()
            self.bar_turn.release()

    def bar(self, printBar: Callable[[], None]) -> None:
        for _ in range(self.n):
            self.bar_turn.acquire()
            printBar()
            self.foo_turn.release()

