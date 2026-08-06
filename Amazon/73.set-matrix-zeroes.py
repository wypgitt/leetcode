#
# @lc app=leetcode id=73 lang=python3
#
# [73] Set Matrix Zeroes
#
# https://leetcode.com/problems/set-matrix-zeroes/description/
#
# algorithms
# Medium (62.83%)
# Likes:    17161
# Dislikes: 867
# Total Accepted:    2.6M
# Total Submissions: 4.1M
# Testcase Example:  '[[1,1,1],[1,0,1],[1,1,1]]'
#
# Given an m x n integer matrix matrix, if an element is 0, set its entire row
# and column to 0's.
# 
# You must do it in place.
# 
# 
# Example 1:
# 
# 
# Input: matrix = [[1,1,1],[1,0,1],[1,1,1]]
# Output: [[1,0,1],[0,0,0],[1,0,1]]
# 
# 
# Example 2:
# 
# 
# Input: matrix = [[0,1,2,0],[3,4,5,2],[1,3,1,5]]
# Output: [[0,0,0,0],[0,4,5,0],[0,3,1,0]]
# 
# 
# 
# Constraints:
# 
# 
# m == matrix.length
# n == matrix[0].length
# 1 <= m, n <= 200
# -2^31 <= matrix[i][j] <= 2^31 - 1
# 
# 
# 
# Follow up:
# 
# 
# A straightforward solution using O(mn) space is probably a bad idea.
# A simple improvement uses O(m + n) space, but still not the best
# solution.
# Could you devise a constant space solution?
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def setZeroes(self, matrix: List[List[int]]) -> None:
        """
        Do not return anything, modify matrix in-place instead.

        Interview explanation:
        Use the first row and first column as marker arrays. A separate boolean
        records whether the first column itself must be zeroed, because
        matrix[0][0] is shared by first-row and first-column markers.

        Edge cases and tests:
        - Zero in first row.
        - Zero in first column.
        - Multiple zeros marking overlapping rows/columns.

        Complexity: O(m*n) time, O(1) extra space.
        """
        m, n = len(matrix), len(matrix[0])
        first_col_zero = any(matrix[r][0] == 0 for r in range(m))
        first_row_zero = any(matrix[0][c] == 0 for c in range(n))

        for r in range(1, m):
            for c in range(1, n):
                if matrix[r][c] == 0:
                    matrix[r][0] = 0
                    matrix[0][c] = 0

        for r in range(1, m):
            for c in range(1, n):
                if matrix[r][0] == 0 or matrix[0][c] == 0:
                    matrix[r][c] = 0

        if first_row_zero:
            for c in range(n):
                matrix[0][c] = 0
        if first_col_zero:
            for r in range(m):
                matrix[r][0] = 0
# @lc code=end


