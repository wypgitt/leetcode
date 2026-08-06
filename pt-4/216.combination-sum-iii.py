"""
Approach: Backtracking over numbers 1 through 9 with pruning.
Data structure: a path list stores the current combination while recursion explores candidates in increasing order.
Interview logic: increasing candidates prevent duplicates. Stop when k numbers are chosen; the path is valid only if the remaining sum is zero. Prune branches where the remaining sum is negative or not enough numbers remain.
Complexity: O(C(9,k) * k) time to output combinations, O(k) recursion space excluding output.
Tests and edge cases: impossible sums return []; k=1; target too small or too large prunes quickly.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def combinationSum3(self, k: int, n: int) -> List[List[int]]:
        ans, path = [], []
        def dfs(start: int, remaining: int) -> None:
            if len(path) == k:
                if remaining == 0:
                    ans.append(path[:])
                return
            need = k - len(path)
            for num in range(start, 10):
                if num > remaining:
                    break
                if 10 - num < need:
                    break
                path.append(num)
                dfs(num + 1, remaining - num)
                path.pop()
        dfs(1, n)
        return ans
# @lc code=end
