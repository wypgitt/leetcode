#
# @lc app=leetcode id=1727 lang=python3
#
# [1727] Largest Submatrix With Rearrangements
#
# https://leetcode.com/problems/largest-submatrix-with-rearrangements/description/
#
# algorithms
# Medium (80.19%)
# Likes:    2315
# Dislikes: 133
# Total Accepted:    160K
# Total Submissions: 200K
# Testcase Example:  "[[0,0,1],[1,1,1],[1,0,1]]"
#
# You are given a binary matrix matrix of size m x n, and you are allowed to
# rearrange the columns of the matrix in any order.
#
# Return the area of the largest submatrix within matrix where every element of
# the submatrix is 1 after reordering the columns optimally.
#
# Example 1:
#
# Input: matrix = [[0,0,1],[1,1,1],[1,0,1]]
# Output: 4
# Explanation: You can rearrange the columns as shown above.
# The largest submatrix of 1s, in bold, has an area of 4.
#
# Example 2:
#
# Input: matrix = [[1,0,1,0,1]]
# Output: 3
# Explanation: You can rearrange the columns as shown above.
# The largest submatrix of 1s, in bold, has an area of 3.
#
# Example 3:
#
# Input: matrix = [[1,1,0],[1,0,1]]
# Output: 2
# Explanation: Notice that you must rearrange entire columns, and there is no
# way to make a submatrix of 1s larger than an area of 2.
#
# Constraints:
#
# m == matrix.length
#
# n == matrix[i].length
#
# 1 <= m * n <= 10^5
#
# matrix[i][j] is either 0 or 1.
#

# @lc code=start
from typing import List


class Solution:
    def largestSubmatrix(self, matrix: List[List[int]]) -> int:
        """
        Interview explanation:
        Columns may be rearranged. For each row as bottom, compute consecutive-1
        heights upward; sort heights descending; area = height[j]*(j+1); track max.

        Algorithm:
        - heights[c] += 1 if matrix[r][c] else 0
        - sorted(heights, reverse=True); update ans

        Complexity: O(m * n log n) time, O(n) space.
        """
        if not matrix:
            return 0
        m, n = len(matrix), len(matrix[0])
        heights = [0] * n
        ans = 0
        for r in range(m):
            for c in range(n):
                heights[c] = heights[c] + 1 if matrix[r][c] else 0
            ordered = sorted(heights, reverse=True)
            for i, h in enumerate(ordered):
                ans = max(ans, h * (i + 1))
        return ans
# @lc code=end
