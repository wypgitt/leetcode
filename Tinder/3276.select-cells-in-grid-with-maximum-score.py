#
# @lc app=leetcode id=3276 lang=python3
#
# [3276] Select Cells in Grid With Maximum Score
#
# https://leetcode.com/problems/select-cells-in-grid-with-maximum-score/description/
#
# algorithms
# Hard (15.90%)
# Likes:    230
# Dislikes: 6
# Total Accepted:    12.9K
# Total Submissions: 81.1K
# Testcase Example:  "[[1,2,3],[4,3,2],[1,1,1]]"
#
#
# You are given a 2D matrix grid consisting of positive integers.
#
# You have to select one or more cells from the matrix such that the
# following conditions are satisfied:
#
# No two selected cells are in the same row of the matrix.
#
# The values in the set of selected cells are unique.
#
# Your score will be the sum of the values of the selected cells.
#
# Return the maximum score you can achieve.
#
# Example 1:
#
# Input: grid = [[1,2,3],[4,3,2],[1,1,1]]
#
# Output: 8
#
# Explanation:
#
# We can select the cells with values 1, 3, and 4 that are colored above.
#
# Example 2:
#
# Input: grid = [[8,7,6],[8,3,2]]
#
# Output: 15
#
# Explanation:
#
# We can select the cells with values 7 and 8 that are colored above.
#
# Constraints:
#
# 1 <= grid.length, grid[i].length <= 10
#
# 1 <= grid[i][j] <= 100
#

# @lc code=start

from typing import List
from functools import lru_cache


class Solution:
    def maxScore(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Pick cells with distinct values, at most one per row; maximize sum. Values
        are 1..100 and rows ≤ 10 — DP over value and used-row bitmask.

        Algorithm:
        - For each value v, collect row bitmask of rows containing v.
        - DP(v, mask): skip v, or take v from one free row that has it.
        - Iterate values descending so larger values considered first (optional);
          memoize on (index_in_sorted_values, mask).

        Complexity: O(V * 2^R * R) time, O(V * 2^R) space.
        """
        m = len(grid)
        rows_of: dict[int, int] = {}
        for i, row in enumerate(grid):
            for v in set(row):
                rows_of[v] = rows_of.get(v, 0) | (1 << i)
        values = sorted(rows_of.keys(), reverse=True)

        @lru_cache(None)
        def dp(i: int, mask: int) -> int:
            if i == len(values):
                return 0
            v = values[i]
            best = dp(i + 1, mask)  # skip
            avail = rows_of[v] & ~mask
            bits = avail
            while bits:
                b = bits & -bits
                best = max(best, v + dp(i + 1, mask | b))
                bits -= b
            return best

        return dp(0, 0)
# @lc code=end
