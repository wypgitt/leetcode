#
# @lc app=leetcode id=2510 lang=python3
#
# [2510] Check if There is a Path With Equal Number of 0's And 1's
#
# https://leetcode.com/problems/check-if-there-is-a-path-with-equal-number-of-0s-and-1s/description/
#
# algorithms
# Medium (52.10%)
# Likes:    114
# Dislikes: 5
# Total Accepted:    8.2K
# Total Submissions: 15.8K
# Testcase Example:  "[[0,1,0,0],[0,1,0,0],[1,0,1,0]]"
#
#
# You are given a 0-indexed m x n binary matrix grid. You can move from a
# cell (row, col) to any of the cells (row + 1, col) or (row, col + 1).
#
# Return true if there is a path from (0, 0) to (m - 1, n - 1) that visits
# an equal number of 0's and 1's. Otherwise return false.
#
# Example 1:
#
# Input: grid = [[0,1,0,0],[0,1,0,0],[1,0,1,0]]
# Output: true
# Explanation: The path colored in blue in the above diagram is a valid
# path because we have 3 cells with a value of 1 and 3 with a value of 0.
# Since there is a valid path, we return true.
#
# Example 2:
#
# Input: grid = [[1,1,0],[0,0,1],[1,0,0]]
# Output: false
# Explanation: There is no path in this grid with an equal number of 0's
# and 1's.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 2 <= m, n <= 100
#
# grid[i][j] is either 0 or 1.
#
# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def isThereAPath(self, grid: List[List[int]]) -> bool:
        """
        Interview explanation:
        Premium. Path from (0,0) to (m-1,n-1) moving only right/down with equal
        number of 0s and 1s along the path.

        Algorithm:
        - Path length m+n-1 must be even. DFS+memo on (r,c,bal) where bal =
          (#1 - #0) so far; prune when |bal| exceeds remaining steps.

        Complexity: O(m*n*(m+n)) time/space.
        """
        return self.isThereAPath_dfs(grid)

    def isThereAPath_dfs(self, grid: List[List[int]]) -> bool:
        """
        Interview explanation:
        Memoized DFS balance search for equal 0/1 path.

        Algorithm:
        - After including cell, bal += 1 if 1 else -1; succeed at end iff bal==0.

        Complexity: O(m*n*(m+n)) time/space.
        """
        m, n = len(grid), len(grid[0])
        if (m + n - 1) % 2:
            return False

        @lru_cache(None)
        def dfs(r: int, c: int, bal: int) -> bool:
            bal += 1 if grid[r][c] == 1 else -1
            rem = (m - 1 - r) + (n - 1 - c)
            if abs(bal) > rem:
                return False
            if r == m - 1 and c == n - 1:
                return bal == 0
            if r + 1 < m and dfs(r + 1, c, bal):
                return True
            if c + 1 < n and dfs(r, c + 1, bal):
                return True
            return False

        return dfs(0, 0, 0)
# @lc code=end
