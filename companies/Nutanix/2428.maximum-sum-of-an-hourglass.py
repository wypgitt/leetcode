#
# @lc app=leetcode id=2428 lang=python3
#
# [2428] Maximum Sum of an Hourglass
#
# https://leetcode.com/problems/maximum-sum-of-an-hourglass/description/
#
# algorithms
# Medium (76.88%)
# Likes:    503
# Dislikes: 73
# Total Accepted:    58.3K
# Total Submissions: 75.8K
# Testcase Example:  "[[6,2,1,3],[4,2,1,5],[9,2,8,7],[4,1,2,9]]"
#
# You are given an m x n integer matrix grid.
#
# We define an hourglass as a part of the matrix with the following form:
#
# Return the maximum sum of the elements of an hourglass.
#
# Note that an hourglass cannot be rotated and must be entirely contained within
# the matrix.
#
#
#
# Example 1:
#
# Input: grid = [[6,2,1,3],[4,2,1,5],[9,2,8,7],[4,1,2,9]]
# Output: 30
# Explanation: The cells shown above represent the hourglass with the maximum
# sum: 6 + 2 + 1 + 2 + 9 + 2 + 8 = 30.
#
# Example 2:
#
# Input: grid = [[1,2,3],[4,5,6],[7,8,9]]
# Output: 35
# Explanation: There is only one hourglass in the matrix, with the sum: 1 + 2 +
# 3 + 5 + 7 + 8 + 9 = 35.
#
#
#
# Constraints:
#
#
# m == grid.length
#
#
# n == grid[i].length
#
#
# 3 <= m, n <= 150
#
#
# 0 <= grid[i][j] <= 10^6
#

# @lc code=start
from typing import List


class Solution:
    def maxSum(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Max sum of an hourglass shape (3x3 without middle-sides) in the grid.

        Algorithm:
        - Enumerate top-left of every 3x3; sum the 7 hourglass cells; track max.

        Complexity: O(mn) time, O(1) space.
        """
        m, n = len(grid), len(grid[0])
        ans = float("-inf")
        for i in range(m - 2):
            for j in range(n - 2):
                s = (
                    grid[i][j]
                    + grid[i][j + 1]
                    + grid[i][j + 2]
                    + grid[i + 1][j + 1]
                    + grid[i + 2][j]
                    + grid[i + 2][j + 1]
                    + grid[i + 2][j + 2]
                )
                ans = max(ans, s)
        return int(ans)
# @lc code=end
