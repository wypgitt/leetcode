from __future__ import annotations

from typing import List


class Solution:
    def largest1BorderedSquare(self, grid: List[List[int]]) -> int:
        rows = len(grid)
        cols = len(grid[0])
        horizontal = [[0] * cols for _ in range(rows)]
        vertical = [[0] * cols for _ in range(rows)]
        best_side = 0

        for r in range(rows):
            for c in range(cols):
                if grid[r][c] == 1:
                    horizontal[r][c] = (horizontal[r][c - 1] if c else 0) + 1
                    vertical[r][c] = (vertical[r - 1][c] if r else 0) + 1
                    side = min(horizontal[r][c], vertical[r][c])
                    while side > best_side:
                        if (
                            vertical[r][c - side + 1] >= side
                            and horizontal[r - side + 1][c] >= side
                        ):
                            best_side = side
                            break
                        side -= 1

        return best_side * best_side

