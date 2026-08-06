#
# @lc app=leetcode id=766 lang=python3
#
# [766] Toeplitz Matrix
#
# https://leetcode.com/problems/toeplitz-matrix/description/
#
# algorithms
# Easy (69.83%)
# Likes:    3755
# Dislikes: 181
# Total Accepted:    474K
# Total Submissions: 678K
# Testcase Example:  "[[1,2,3,4],[5,1,2,3],[9,5,1,2]]"
#
# Given an m x n matrix, return true if the matrix is Toeplitz. Otherwise,
# return false.
#
# A matrix is Toeplitz if every diagonal from top-left to bottom-right has the
# same elements.
#
# Example 1:
#
# Input: matrix = [[1,2,3,4],[5,1,2,3],[9,5,1,2]]
# Output: true
# Explanation:
# In the above grid, the diagonals are:
# "[9]", "[5, 5]", "[1, 1, 1]", "[2, 2, 2]", "[3, 3]", "[4]".
# In each diagonal all elements are the same, so the answer is True.
#
# Example 2:
#
# Input: matrix = [[1,2],[2,2]]
# Output: false
# Explanation:
# The diagonal "[1, 2]" has different elements.
#
# Constraints:
#
# m == matrix.length
#
# n == matrix[i].length
#
# 1 <= m, n <= 20
#
# 0 <= matrix[i][j] <= 99
#
# Follow up:
#
# What if the matrix is stored on disk, and the memory is limited such that you
# can only load at most one row of the matrix into the memory at once?
#
# What if the matrix is so large that you can only load up a partial row into
# the memory at once?
#


# @lc code=start
from typing import List


class Solution:
    def isToeplitzMatrix(self, matrix: List[List[int]]) -> bool:
        """
        Interview explanation:
        A Toeplitz matrix has equal diagonals: every matrix[r][c] must equal
        matrix[r-1][c-1] when that neighbor exists.

        Algorithm:
        - For r,c from 1..: if matrix[r][c] != matrix[r-1][c-1]: False

        Complexity: O(mn) time, O(1) space.
        """
        for r in range(1, len(matrix)):
            for c in range(1, len(matrix[0])):
                if matrix[r][c] != matrix[r - 1][c - 1]:
                    return False
        return True
# @lc code=end

