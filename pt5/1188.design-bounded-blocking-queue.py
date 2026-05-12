from __future__ import annotations

from collections import deque
from threading import Condition


class BoundedBlockingQueue(object):
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.queue = deque()
        self.condition = Condition()

    def enqueue(self, element: int) -> None:
        with self.condition:
            while len(self.queue) == self.capacity:
                self.condition.wait()
            self.queue.appendleft(element)
            self.condition.notify_all()

    def dequeue(self) -> int:
        with self.condition:
            while not self.queue:
                self.condition.wait()
            value = self.queue.pop()
            self.condition.notify_all()
            return value

    def size(self) -> int:
        with self.condition:
            return len(self.queue)

