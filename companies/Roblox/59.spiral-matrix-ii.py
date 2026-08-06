#
# @lc app=leetcode id=59 lang=python3
#
# [59] Spiral Matrix II
#
# https://leetcode.com/problems/spiral-matrix-ii/description/
#
# algorithms
# Medium (74.99%)
# Likes:    6923
# Dislikes: 289
# Total Accepted:    806.4K
# Total Submissions: 1.1M
# Testcase Example:  '3'
#
# Given a positive integer n, generate an n x n matrix filled with elements
# from 1 to n^2 in spiral order.
# 
# 
# Example 1:
# 
# 
# Input: n = 3
# Output: [[1,2,3],[8,9,4],[7,6,5]]
# 
# 
# Example 2:
# 
# 
# Input: n = 1
# Output: [[1]]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 20
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def generateMatrix(self, n: int) -> List[List[int]]:
        """
        Interview explanation:
        This is the constructive version of spiral traversal. Use four shrinking
        boundaries and fill numbers from 1 to n^2 while walking right, down,
        left, and up. The matrix itself stores the answer; no extra visited set
        is needed because boundaries prevent revisits.

        Edge cases and tests:
        - n=1 returns [[1]].
        - Odd n leaves a center cell filled last.
        - Even n finishes after the innermost 2x2 layer.

        Complexity: O(n^2) time and O(1) extra space excluding output.
        """
        matrix = [[0] * n for _ in range(n)]
        top, bottom = 0, n - 1
        left, right = 0, n - 1
        value = 1

        while top <= bottom and left <= right:
            for c in range(left, right + 1):
                matrix[top][c] = value
                value += 1
            top += 1
            for r in range(top, bottom + 1):
                matrix[r][right] = value
                value += 1
            right -= 1
            for c in range(right, left - 1, -1):
                matrix[bottom][c] = value
                value += 1
            bottom -= 1
            for r in range(bottom, top - 1, -1):
                matrix[r][left] = value
                value += 1
            left += 1

        return matrix
# @lc code=end


