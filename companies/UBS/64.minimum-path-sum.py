#
# @lc app=leetcode id=64 lang=python3
#
# [64] Minimum Path Sum
#
# https://leetcode.com/problems/minimum-path-sum/description/
#
# algorithms
# Medium (68.17%)
# Likes:    13724
# Dislikes: 203
# Total Accepted:    1.9M
# Total Submissions: 2.7M
# Testcase Example:  '[[1,3,1],[1,5,1],[4,2,1]]'
#
# Given a m x n grid filled with non-negative numbers, find a path from top
# left to bottom right, which minimizes the sum of all numbers along its path.
# 
# Note: You can only move either down or right at any point in time.
# 
# 
# Example 1:
# 
# 
# Input: grid = [[1,3,1],[1,5,1],[4,2,1]]
# Output: 7
# Explanation: Because the path 1 → 3 → 1 → 1 → 1 minimizes the sum.
# 
# 
# Example 2:
# 
# 
# Input: grid = [[1,2,3],[4,5,6]]
# Output: 12
# 
# 
# 
# Constraints:
# 
# 
# m == grid.length
# n == grid[i].length
# 1 <= m, n <= 200
# 0 <= grid[i][j] <= 200
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def minPathSum(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        The optimal cost to a cell is its value plus the cheaper of the optimal
        costs from above or left. A one-dimensional DP array stores the best cost
        for the current row, updating left to right.

        Edge cases and tests:
        - 1x1 grid returns its only value.
        - First row can only come from the left.
        - First column can only come from above.

        Complexity: O(m*n) time, O(n) space.
        """
        m, n = len(grid), len(grid[0])
        dp = [0] * n
        for r in range(m):
            for c in range(n):
                if r == 0 and c == 0:
                    dp[c] = grid[r][c]
                elif r == 0:
                    dp[c] = dp[c - 1] + grid[r][c]
                elif c == 0:
                    dp[c] = dp[c] + grid[r][c]
                else:
                    dp[c] = min(dp[c], dp[c - 1]) + grid[r][c]
        return dp[-1]
# @lc code=end


