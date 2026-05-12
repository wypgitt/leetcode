from __future__ import annotations

from threading import Semaphore
from typing import Callable


class ZeroEvenOdd:
    def __init__(self, n):
        self.n = n
        self.zero_turn = Semaphore(1)
        self.odd_turn = Semaphore(0)
        self.even_turn = Semaphore(0)

    def zero(self, printNumber: Callable[[int], None]) -> None:
        for value in range(1, self.n + 1):
            self.zero_turn.acquire()
            printNumber(0)
            if value % 2:
                self.odd_turn.release()
            else:
                self.even_turn.release()

    def even(self, printNumber: Callable[[int], None]) -> None:
        for value in range(2, self.n + 1, 2):
            self.even_turn.acquire()
            printNumber(value)
            self.zero_turn.release()

    def odd(self, printNumber: Callable[[int], None]) -> None:
        for value in range(1, self.n + 1, 2):
            self.odd_turn.acquire()
            printNumber(value)
            self.zero_turn.release()

