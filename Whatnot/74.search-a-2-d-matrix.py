#
# @lc app=leetcode id=74 lang=python3
#
# [74] Search a 2D Matrix
#
# https://leetcode.com/problems/search-a-2d-matrix/description/
#
# algorithms
# Medium (53.88%)
# Likes:    17962
# Dislikes: 486
# Total Accepted:    2.9M
# Total Submissions: 5.4M
# Testcase Example:  '[[1,3,5,7],[10,11,16,20],[23,30,34,60]]\n3'
#
# You are given an m x n integer matrix matrix with the following two
# properties:
# 
# 
# Each row is sorted in non-decreasing order.
# The first integer of each row is greater than the last integer of the
# previous row.
# 
# 
# Given an integer target, return true if target is in matrix or false
# otherwise.
# 
# You must write a solution in O(log(m * n)) time complexity.
# 
# 
# Example 1:
# 
# 
# Input: matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 3
# Output: true
# 
# 
# Example 2:
# 
# 
# Input: matrix = [[1,3,5,7],[10,11,16,20],[23,30,34,60]], target = 13
# Output: false
# 
# 
# 
# Constraints:
# 
# 
# m == matrix.length
# n == matrix[i].length
# 1 <= m, n <= 100
# -10^4 <= matrix[i][j], target <= 10^4
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        """
        Interview explanation:
        The matrix is globally sorted if viewed as one flattened array: row ends
        are less than the next row starts. Binary search over indices [0, m*n)
        maps mid to row mid // n and column mid % n.

        Edge cases and tests:
        - Target less than first or greater than last returns False.
        - Single row or single column works with the same mapping.
        - Exact first/last element returns True.

        Complexity: O(log(m*n)) time, O(1) space.
        """
        m, n = len(matrix), len(matrix[0])
        left, right = 0, m * n - 1

        while left <= right:
            mid = (left + right) // 2
            value = matrix[mid // n][mid % n]
            if value == target:
                return True
            if value < target:
                left = mid + 1
            else:
                right = mid - 1

        return False
# @lc code=end


