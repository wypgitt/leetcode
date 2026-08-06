#
# @lc app=leetcode id=63 lang=python3
#
# [63] Unique Paths II
#
# https://leetcode.com/problems/unique-paths-ii/description/
#
# algorithms
# Medium (44.44%)
# Likes:    9721
# Dislikes: 562
# Total Accepted:    1.5M
# Total Submissions: 3.3M
# Testcase Example:  '[[0,0,0],[0,1,0],[0,0,0]]'
#
# You are given an m x n integer array grid. There is a robot initially located
# at the top-left corner (i.e., grid[0][0]). The robot tries to move to the
# bottom-right corner (i.e., grid[m - 1][n - 1]). The robot can only move
# either down or right at any point in time.
# 
# An obstacle and space are marked as 1 or 0 respectively in grid. A path that
# the robot takes cannot include any square that is an obstacle.
# 
# Return the number of possible unique paths that the robot can take to reach
# the bottom-right corner.
# 
# The testcases are generated so that the answer will be less than or equal to
# 2 * 10^9.
# 
# 
# Example 1:
# 
# 
# Input: obstacleGrid = [[0,0,0],[0,1,0],[0,0,0]]
# Output: 2
# Explanation: There is one obstacle in the middle of the 3x3 grid above.
# There are two ways to reach the bottom-right corner:
# 1. Right -> Right -> Down -> Down
# 2. Down -> Down -> Right -> Right
# 
# 
# Example 2:
# 
# 
# Input: obstacleGrid = [[0,1],[0,0]]
# Output: 1
# 
# 
# 
# Constraints:
# 
# 
# m == obstacleGrid.length
# n == obstacleGrid[i].length
# 1 <= m, n <= 100
# obstacleGrid[i][j] is 0 or 1.
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def uniquePathsWithObstacles(self, obstacleGrid: List[List[int]]) -> int:
        """
        Interview explanation:
        This is unique paths with blocked cells. The same one-dimensional DP
        works: dp[c] stores ways to reach the current row's column c. An obstacle
        resets dp[c] to 0 because no path can stand on that cell.

        Edge cases and tests:
        - Obstacle at start or end returns 0.
        - Single open cell returns 1.
        - Obstacles in first row/column correctly zero all cells beyond them.

        Complexity: O(m*n) time, O(n) space.
        """
        m, n = len(obstacleGrid), len(obstacleGrid[0])
        dp = [0] * n
        dp[0] = 1 if obstacleGrid[0][0] == 0 else 0

        for r in range(m):
            for c in range(n):
                if obstacleGrid[r][c] == 1:
                    dp[c] = 0
                elif c > 0:
                    dp[c] += dp[c - 1]

        return dp[-1]
# @lc code=end


