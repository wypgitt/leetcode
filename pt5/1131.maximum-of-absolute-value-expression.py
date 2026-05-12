from __future__ import annotations

from typing import List


class Solution:
    def maxAbsValExpr(self, arr1: List[int], arr2: List[int]) -> int:
        best = 0

        for sign1 in (1, -1):
            for sign2 in (1, -1):
                smallest = float("inf")
                largest = float("-inf")
                for i, (a, b) in enumerate(zip(arr1, arr2)):
                    value = sign1 * a + sign2 * b + i
                    smallest = min(smallest, value)
                    largest = max(largest, value)
                best = max(best, largest - smallest)

        return best

