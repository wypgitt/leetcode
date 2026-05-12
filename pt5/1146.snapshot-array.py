from __future__ import annotations

from bisect import bisect_right
from typing import List, Tuple


class SnapshotArray:
    def __init__(self, length: int):
        self.snap_id = 0
        self.history: List[List[Tuple[int, int]]] = [[(0, 0)] for _ in range(length)]

    def set(self, index: int, val: int) -> None:
        if self.history[index][-1][0] == self.snap_id:
            self.history[index][-1] = (self.snap_id, val)
        else:
            self.history[index].append((self.snap_id, val))

    def snap(self) -> int:
        current = self.snap_id
        self.snap_id += 1
        return current

    def get(self, index: int, snap_id: int) -> int:
        records = self.history[index]
        position = bisect_right(records, (snap_id, float("inf"))) - 1
        return records[position][1]

