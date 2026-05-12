from __future__ import annotations

from collections import deque
from typing import Deque, Set, Tuple


class Solution:
    def minKnightMoves(self, x: int, y: int) -> int:
        x, y = abs(x), abs(y)
        if x == 0 and y == 0:
            return 0

        moves = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
        queue: Deque[Tuple[int, int, int]] = deque([(0, 0, 0)])
        visited: Set[Tuple[int, int]] = {(0, 0)}

        while queue:
            row, col, distance = queue.popleft()
            for dr, dc in moves:
                nr, nc = row + dr, col + dc
                if (nr, nc) == (x, y):
                    return distance + 1
                if -2 <= nr <= x + 2 and -2 <= nc <= y + 2 and (nr, nc) not in visited:
                    visited.add((nr, nc))
                    queue.append((nr, nc, distance + 1))

        return -1

