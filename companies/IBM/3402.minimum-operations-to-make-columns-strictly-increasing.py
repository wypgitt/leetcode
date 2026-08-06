#
# @lc app=leetcode id=3402 lang=python3
#
# [3402] Minimum Operations to Make Columns Strictly Increasing
#
# https://leetcode.com/problems/minimum-operations-to-make-columns-strictly-increasing/description/
#
# algorithms
# Easy (72.82%)
# Likes:    68
# Dislikes: 5
# Total Accepted:    39.3K
# Total Submissions: 54K
# Testcase Example:  "[[3,2],[1,3],[3,4],[0,1]]"
#
#
# You are given a m x n matrix grid consisting of non-negative integers.
#
# In one operation, you can increment the value of any grid[i][j] by 1.
#
# Return the minimum number of operations needed to make all columns of
# grid strictly increasing.
#
# Example 1:
#
# Input: grid = [[3,2],[1,3],[3,4],[0,1]]
#
# Output: 15
#
# Explanation:
#
# To make the 0^th column strictly increasing, we can apply 3 operations
# on grid[1][0], 2 operations on grid[2][0], and 6 operations on
# grid[3][0].
#
# To make the 1^st column strictly increasing, we can apply 4 operations
# on grid[3][1].
#
# Example 2:
#
# Input: grid = [[3,2,1],[2,1,0],[1,2,3]]
#
# Output: 12
#
# Explanation:
#
# To make the 0^th column strictly increasing, we can apply 2 operations
# on grid[1][0], and 4 operations on grid[2][0].
#
# To make the 1^st column strictly increasing, we can apply 2 operations
# on grid[1][1], and 2 operations on grid[2][1].
#
# To make the 2^nd column strictly increasing, we can apply 2 operations
# on grid[1][2].
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 1 <= m, n <= 50
#
# 0 <= grid[i][j] < 2500
#

# @lc code=start
from typing import List


class Solution:
    def minimumOperations(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Make every column strictly increasing using only +1 operations.
        Process each column top-to-bottom, lifting each cell just enough
        above the previous cell.

        Algorithm:
        - For each column, track prev; if cur <= prev, add (prev+1-cur)
          ops and set cur = prev+1; else prev = cur.

        Complexity: O(m*n) time, O(1) extra space.
        """
        m, n = len(grid), len(grid[0])
        ops = 0
        for c in range(n):
            prev = grid[0][c]
            for r in range(1, m):
                cur = grid[r][c]
                if cur <= prev:
                    ops += prev + 1 - cur
                    prev = prev + 1
                else:
                    prev = cur
        return ops
# @lc code=end
