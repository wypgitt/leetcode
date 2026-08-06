"""
Approach: Maintain row and column pointers and skip empty rows lazily.
Data structure: two indexes avoid flattening the whole 2D vector, so memory usage stays constant.
Interview logic: hasNext advances to the next row that still has elements. next calls hasNext to normalize the cursor, returns the current value, then advances the column.
Complexity: O(1) amortized time per operation, O(1) extra space.
Tests and edge cases: leading/trailing empty rows; consecutive empty rows; repeated hasNext calls should not advance past a valid element.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Vector2D:
    def __init__(self, vec: List[List[int]]):
        self.vec = vec
        self.row = 0
        self.col = 0

    def _skip_empty(self) -> None:
        while self.row < len(self.vec) and self.col >= len(self.vec[self.row]):
            self.row += 1
            self.col = 0

    def next(self) -> int:
        self._skip_empty()
        val = self.vec[self.row][self.col]
        self.col += 1
        return val

    def hasNext(self) -> bool:
        self._skip_empty()
        return self.row < len(self.vec)
# @lc code=end
