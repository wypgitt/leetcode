#
# @lc app=leetcode id=62 lang=python3
#
# [62] Unique Paths
#
# https://leetcode.com/problems/unique-paths/description/
#
# algorithms
# Medium (66.81%)
# Likes:    18412
# Dislikes: 496
# Total Accepted:    2.8M
# Total Submissions: 4.2M
# Testcase Example:  '3\n7'
#
# There is a robot on an m x n grid. The robot is initially located at the
# top-left corner (i.e., grid[0][0]). The robot tries to move to the
# bottom-right corner (i.e., grid[m - 1][n - 1]). The robot can only move
# either down or right at any point in time.
# 
# Given the two integers m and n, return the number of possible unique paths
# that the robot can take to reach the bottom-right corner.
# 
# The test cases are generated so that the answer will be less than or equal to
# 2 * 10^9.
# 
# 
# Example 1:
# 
# 
# Input: m = 3, n = 7
# Output: 28
# 
# 
# Example 2:
# 
# 
# Input: m = 3, n = 2
# Output: 3
# Explanation: From the top-left corner, there are a total of 3 ways to reach
# the bottom-right corner:
# 1. Right -> Down -> Down
# 2. Down -> Down -> Right
# 3. Down -> Right -> Down
# 
# 
# 
# Constraints:
# 
# 
# 1 <= m, n <= 100
# 
# 
#

# @lc code=start
from typing import List, Optional
class Solution:
    def uniquePaths(self, m: int, n: int) -> int:
        """
        Interview explanation:
        Dynamic programming works because the number of ways to a cell is the
        sum of ways from the cell above and the cell to the left. A one-row DP
        array is enough because each row only depends on the current left value
        and the previous row's same column value.

        Edge cases and tests:
        - One row or one column has exactly one path.
        - Small grid 3x2 returns 3.
        - Symmetry: uniquePaths(m, n) == uniquePaths(n, m).

        Complexity: O(m*n) time, O(n) space.
        """
        dp = [1] * n
        for _ in range(1, m):
            for c in range(1, n):
                dp[c] += dp[c - 1]
        return dp[-1]
# @lc code=end


