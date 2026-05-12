from __future__ import annotations

from typing import List


class Solution:
    def maximumSum(self, arr: List[int]) -> int:
        no_delete = arr[0]
        one_delete = float("-inf")
        best = arr[0]

        for value in arr[1:]:
            one_delete = max(one_delete + value, no_delete)
            no_delete = max(no_delete + value, value)
            best = max(best, no_delete, one_delete)

        return best

