"""
Approach: Store (value, minimum_so_far) at every stack level.
Data structure: an augmented stack preserves normal push/pop order and gives O(1) minimum queries.
Interview logic: when the current minimum is popped, the previous minimum is already stored in the tuple beneath it.
Complexity: O(1) per operation, O(n) space.
Tests and edge cases: duplicate minima; negative values; popping the current minimum reveals the previous one.
"""
from __future__ import annotations

# @lc code=start
class MinStack:
    def __init__(self):
        self.stack = []

    def push(self, val: int) -> None:
        current_min = val if not self.stack else min(val, self.stack[-1][1])
        self.stack.append((val, current_min))

    def pop(self) -> None:
        self.stack.pop()

    def top(self) -> int:
        return self.stack[-1][0]

    def getMin(self) -> int:
        return self.stack[-1][1]
# @lc code=end
