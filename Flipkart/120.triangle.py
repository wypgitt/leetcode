#
# @lc app=leetcode id=120 lang=python3
#
# [120] Triangle
#
# https://leetcode.com/problems/triangle/description/
#
# algorithms
# Medium (59.90%)
# Likes:    10866
# Dislikes: 612
# Total Accepted:    1.3M
# Total Submissions: 2.2M
# Testcase Example:  '[[2],[3,4],[6,5,7],[4,1,8,3]]'
#
# Given a triangle array, return the minimum path sum from top to bottom.
# 
# For each step, you may move to an adjacent number of the row below. More
# formally, if you are on index i on the current row, you may move to either
# index i or index i + 1 on the next row.
# 
# 
# Example 1:
# 
# 
# Input: triangle = [[2],[3,4],[6,5,7],[4,1,8,3]]
# Output: 11
# Explanation: The triangle looks like:
# ⁠  2
# ⁠ 3 4
# ⁠6 5 7
# 4 1 8 3
# The minimum path sum from top to bottom is 2 + 3 + 5 + 1 = 11 (underlined
# above).
# 
# 
# Example 2:
# 
# 
# Input: triangle = [[-10]]
# Output: -10
# 
# 
# 
# Constraints:
# 
# 
# 1 <= triangle.length <= 200
# triangle[0].length == 1
# triangle[i].length == triangle[i - 1].length + 1
# -10^4 <= triangle[i][j] <= 10^4
# 
# 
# 
# Follow up: Could you do this using only O(n) extra space, where n is the
# total number of rows in the triangle?
#

# @lc code=start
from typing import List, Optional
class Solution:
    def minimumTotal(self, triangle: List[List[int]]) -> int:
        """
        Interview explanation:
        Bottom-up DP works because the best path from a cell equals its value
        plus the cheaper best path from the two adjacent cells below. Starting
        from the last row means each update has all information it needs. A
        single array initialized to the bottom row satisfies the O(n) follow-up.

        Edge cases and tests:
        - One-row triangle returns that element.
        - Negative values are handled because we use min, not greedy positivity.
        - Uneven row lengths follow the triangle rule by construction.

        Complexity: O(total cells) time, O(number of rows) space.
        """
        dp = triangle[-1][:]
        for r in range(len(triangle) - 2, -1, -1):
            for c in range(len(triangle[r])):
                dp[c] = triangle[r][c] + min(dp[c], dp[c + 1])
        return dp[0]
# @lc code=end


