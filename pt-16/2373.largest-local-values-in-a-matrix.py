#
# @lc app=leetcode id=2373 lang=python3
#
# [2373] Largest Local Values in a Matrix
#
# https://leetcode.com/problems/largest-local-values-in-a-matrix/description/
#
# algorithms
# Easy (87.67%)
# Likes:    1339
# Dislikes: 184
# Total Accepted:    206K
# Total Submissions: 235K
# Testcase Example:  "[[9,9,8,1],[5,6,2,6],[8,2,6,4],[6,2,2,2]]"
#
# You are given an n x n integer matrix grid.
#
# Generate an integer matrix maxLocal of size (n - 2) x (n - 2) such that:
#
#
# maxLocal[i][j] is equal to the largest value of the 3 x 3 matrix in grid
# centered around row i + 1 and column j + 1.
#
# In other words, we want to find the largest value in every contiguous 3 x 3
# matrix in grid.
#
# Return the generated matrix.
#
#
#
# Example 1:
#
# Input: grid = [[9,9,8,1],[5,6,2,6],[8,2,6,4],[6,2,2,2]]
# Output: [[9,9],[8,6]]
# Explanation: The diagram above shows the original matrix and the generated
# matrix.
# Notice that each value in the generated matrix corresponds to the largest
# value of a contiguous 3 x 3 matrix in grid.
#
# Example 2:
#
# Input: grid = [[1,1,1,1,1],[1,1,1,1,1],[1,1,2,1,1],[1,1,1,1,1],[1,1,1,1,1]]
# Output: [[2,2,2],[2,2,2],[2,2,2]]
# Explanation: Notice that the 2 is contained within every contiguous 3 x 3
# matrix in grid.
#
#
#
# Constraints:
#
#
# n == grid.length == grid[i].length
#
#
# 3 <= n <= 100
#
#
# 1 <= grid[i][j] <= 100
#

# @lc code=start

from typing import List


class Solution:
    def largestLocal(self, grid: List[List[int]]) -> List[List[int]]:
        """
        Interview explanation:
        For n x n grid, return (n-2)x(n-2) where each cell is max of the 3x3
        centered at (i+1, j+1).

        Algorithm:
        - For each output cell scan its 3x3 window for maximum.

        Complexity: O(n^2) time, O(n^2) space for answer.
        """
        n = len(grid)
        ans = [[0] * (n - 2) for _ in range(n - 2)]
        for i in range(n - 2):
            for j in range(n - 2):
                m = 0
                for x in range(i, i + 3):
                    for y in range(j, j + 3):
                        m = max(m, grid[x][y])
                ans[i][j] = m
        return ans
# @lc code=end
