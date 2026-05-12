from __future__ import annotations

from threading import Condition
from typing import Callable


class FizzBuzz:
    def __init__(self, n: int):
        self.n = n
        self.current = 1
        self.condition = Condition()

    def _run_when(self, predicate, action) -> None:
        while True:
            with self.condition:
                while self.current <= self.n and not predicate(self.current):
                    self.condition.wait()
                if self.current > self.n:
                    self.condition.notify_all()
                    return
                action(self.current)
                self.current += 1
                self.condition.notify_all()

    def fizz(self, printFizz: Callable[[], None]) -> None:
        self._run_when(lambda value: value % 3 == 0 and value % 5 != 0, lambda _: printFizz())

    def buzz(self, printBuzz: Callable[[], None]) -> None:
        self._run_when(lambda value: value % 5 == 0 and value % 3 != 0, lambda _: printBuzz())

    def fizzbuzz(self, printFizzBuzz: Callable[[], None]) -> None:
        self._run_when(lambda value: value % 15 == 0, lambda _: printFizzBuzz())

    def number(self, printNumber: Callable[[int], None]) -> None:
        self._run_when(lambda value: value % 3 != 0 and value % 5 != 0, printNumber)

