#
# @lc app=leetcode id=3148 lang=python3
#
# [3148] Maximum Difference Score in a Grid
#
# https://leetcode.com/problems/maximum-difference-score-in-a-grid/description/
#
# algorithms
# Medium (47.90%)
# Likes:    296
# Dislikes: 23
# Total Accepted:    25K
# Total Submissions: 52.3K
# Testcase Example:  "[[9,5,7,3],[8,9,6,1],[6,7,14,3],[2,5,3,1]]"
#
#
# You are given an m x n matrix grid consisting of positive integers. You
# can move from a cell in the matrix to any other cell that is either to
# the bottom or to the right (not necessarily adjacent). The score of a
# move from a cell with the value c1 to a cell with the value c2 is c2 -
# c1.
#
# You can start at any cell, and you have to make at least one move.
#
# Return the maximum total score you can achieve.
#
# Example 1:
#
# Input: grid = [[9,5,7,3],[8,9,6,1],[6,7,14,3],[2,5,3,1]]
#
# Output: 9
#
# Explanation: We start at the cell (0, 1), and we perform the following
# moves:
#
# - Move from the cell (0, 1) to (2, 1) with a score of 7 - 5 = 2.
#
# - Move from the cell (2, 1) to (2, 2) with a score of 14 - 7 = 7.
#
# The total score is 2 + 7 = 9.
#
# Example 2:
#
# Input: grid = [[4,3,2],[3,2,1]]
#
# Output: -1
#
# Explanation: We start at the cell (0, 0), and we perform one move: (0,
# 0) to (0, 1). The score is 3 - 4 = -1.
#
# Constraints:
#
# m == grid.length
#
# n == grid[i].length
#
# 2 <= m, n <= 1000
#
# 4 <= m * n <= 10^5
#
# 1 <= grid[i][j] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def maxScore(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Moves only down/right; path score telescopes to end - start. Maximize
        grid[end] - grid[start] over distinct cells with start able to reach end.

        Algorithm:
        - min_upto[i][j] = min in the rectangle [0..i] x [0..j].
        - For cell (i,j), best start min is min(min_upto above, min_upto left).
        - Track max of grid[i][j] - that previous min.

        Complexity: O(m * n) time, O(m * n) space.
        """
        m, n = len(grid), len(grid[0])
        ans = float("-inf")
        min_upto = [[0] * n for _ in range(m)]
        min_upto[0][0] = grid[0][0]
        for j in range(1, n):
            ans = max(ans, grid[0][j] - min_upto[0][j - 1])
            min_upto[0][j] = min(min_upto[0][j - 1], grid[0][j])
        for i in range(1, m):
            ans = max(ans, grid[i][0] - min_upto[i - 1][0])
            min_upto[i][0] = min(min_upto[i - 1][0], grid[i][0])
            for j in range(1, n):
                prev = min(min_upto[i - 1][j], min_upto[i][j - 1])
                ans = max(ans, grid[i][j] - prev)
                min_upto[i][j] = min(prev, grid[i][j])
        return int(ans)
# @lc code=end
