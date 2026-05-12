from __future__ import annotations

from typing import List


class Solution:
    def mctFromLeafValues(self, arr: List[int]) -> int:
        stack = [float("inf")]
        cost = 0

        for value in arr:
            while stack[-1] <= value:
                middle = stack.pop()
                cost += middle * min(stack[-1], value)
            stack.append(value)

        while len(stack) > 2:
            cost += stack.pop() * stack[-1]

        return cost

