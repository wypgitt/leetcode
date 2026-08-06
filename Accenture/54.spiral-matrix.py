#
# @lc app=leetcode id=54 lang=python3
#
# [54] Spiral Matrix
#
# https://leetcode.com/problems/spiral-matrix/description/
#
# algorithms
# Medium (56.69%)
# Likes:    17510
# Dislikes: 1573
# Total Accepted:    2.4M
# Total Submissions: 4.2M
# Testcase Example:  '[[1,2,3],[4,5,6],[7,8,9]]'
#
# Given an m x n matrix, return all elements of the matrix in spiral order.
# 
# 
# Example 1:
# 
# 
# Input: matrix = [[1,2,3],[4,5,6],[7,8,9]]
# Output: [1,2,3,6,9,8,7,4,5]
# 
# 
# Example 2:
# 
# 
# Input: matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]
# Output: [1,2,3,4,8,12,11,10,9,5,6,7]
# 
# 
# 
# Constraints:
# 
# 
# m == matrix.length
# n == matrix[i].length
# 1 <= m, n <= 10
# -100 <= matrix[i][j] <= 100
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def spiralOrder(self, matrix: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        Maintain four shrinking boundaries: top, bottom, left, and right. Each
        loop consumes the top row, right column, bottom row, and left column in
        order, then moves the boundaries inward. Boundary checks prevent double
        reading the last remaining row or column.

        Edge cases and tests:
        - Single row and single column.
        - Rectangular matrices, not just square.
        - Odd dimensions with one center element.

        Complexity: O(m*n) time, O(1) extra space excluding output.
        """
        ans = []
        top, bottom = 0, len(matrix) - 1
        left, right = 0, len(matrix[0]) - 1

        while top <= bottom and left <= right:
            for c in range(left, right + 1):
                ans.append(matrix[top][c])
            top += 1

            for r in range(top, bottom + 1):
                ans.append(matrix[r][right])
            right -= 1

            if top <= bottom:
                for c in range(right, left - 1, -1):
                    ans.append(matrix[bottom][c])
                bottom -= 1

            if left <= right:
                for r in range(bottom, top - 1, -1):
                    ans.append(matrix[r][left])
                left += 1

        return ans
# @lc code=end


