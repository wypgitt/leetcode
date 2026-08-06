#
# @lc app=leetcode id=2319 lang=python3
#
# [2319] Check if Matrix Is X-Matrix
#
# https://leetcode.com/problems/check-if-matrix-is-x-matrix/description/
#
# algorithms
# Easy (66.91%)
# Likes:    556
# Dislikes: 26
# Total Accepted:    79.4K
# Total Submissions: 118.7K
# Testcase Example:  "[[2,0,0,1],[0,3,1,0],[0,5,2,0],[4,0,0,2]]"
#
# A square matrix is said to be an X-Matrix if both of the following conditions
# hold:
#
#
# All the elements in the diagonals of the matrix are non-zero.
#
#
# All other elements are 0.
#
# Given a 2D integer array grid of size n x n representing a square matrix,
# return true if grid is an X-Matrix. Otherwise, return false.
#
#
#
# Example 1:
#
# Input: grid = [[2,0,0,1],[0,3,1,0],[0,5,2,0],[4,0,0,2]]
# Output: true
# Explanation: Refer to the diagram above.
# An X-Matrix should have the green elements (diagonals) be non-zero and the red
# elements be 0.
# Thus, grid is an X-Matrix.
#
# Example 2:
#
# Input: grid = [[5,7,0],[0,3,1],[0,5,0]]
# Output: false
# Explanation: Refer to the diagram above.
# An X-Matrix should have the green elements (diagonals) be non-zero and the red
# elements be 0.
# Thus, grid is not an X-Matrix.
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
# 0 <= grid[i][j] <= 10^5
#

# @lc code=start
from typing import List


class Solution:
    def checkXMatrix(self, grid: List[List[int]]) -> bool:
        """
        Interview explanation:
        X-matrix: both diagonals are all non-zero; all other cells are zero.

        Algorithm:
        - For each cell (i,j): if on diagonal (i==j or i+j==n-1) require !=0;
          else require ==0.

        Complexity: O(n^2) time, O(1) space.
        """
        n = len(grid)
        for i in range(n):
            for j in range(n):
                if i == j or i + j == n - 1:
                    if grid[i][j] == 0:
                        return False
                elif grid[i][j] != 0:
                    return False
        return True
# @lc code=end
