#
# @lc app=leetcode id=2435 lang=python3
#
# [2435] Paths in Matrix Whose Sum Is Divisible by K
#
# https://leetcode.com/problems/paths-in-matrix-whose-sum-is-divisible-by-k/description/
#
# algorithms
# Hard (58.70%)
# Likes:    1359
# Dislikes: 46
# Total Accepted:    107.2K
# Total Submissions: 182.5K
# Testcase Example:  "[[5,2,4],[3,0,5],[0,7,2]]\n3"
#
# You are given a 0-indexed m x n integer matrix grid and an integer k. You are
# currently at position (0, 0) and you want to reach position (m - 1, n - 1)
# moving only down or right.
#
# Return the number of paths where the sum of the elements on the path is
# divisible by k. Since the answer may be very large, return it modulo 10^9 + 7.
#
#
#
# Example 1:
#
# Input: grid = [[5,2,4],[3,0,5],[0,7,2]], k = 3
# Output: 2
# Explanation: There are two paths where the sum of the elements on the path is
# divisible by k.
# The first path highlighted in red has a sum of 5 + 2 + 4 + 5 + 2 = 18 which is
# divisible by 3.
# The second path highlighted in blue has a sum of 5 + 3 + 0 + 5 + 2 = 15 which
# is divisible by 3.
#
# Example 2:
#
# Input: grid = [[0,0]], k = 5
# Output: 1
# Explanation: The path highlighted in red has a sum of 0 + 0 = 0 which is
# divisible by 5.
#
# Example 3:
#
# Input: grid = [[7,3,4,9],[2,3,6,2],[2,3,7,0]], k = 1
# Output: 10
# Explanation: Every integer is divisible by 1 so the sum of the elements on
# every possible path is divisible by k.
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
# 1 <= m, n <= 5 * 10^4
#
#
# 1 <= m * n <= 5 * 10^4
#
#
# 0 <= grid[i][j] <= 100
#
#
# 1 <= k <= 50
#

# @lc code=start
from typing import List


class Solution:
    def numberOfPaths(self, grid: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Count right/down paths from top-left to bottom-right whose cell-sum is
        divisible by k.

        Algorithm:
        - DP[i][j][r] ways to reach (i,j) with sum % k == r.

        Complexity: O(m*n*k) time/space.
        """
        MOD = 10**9 + 7
        m, n = len(grid), len(grid[0])
        dp = [[[0] * k for _ in range(n)] for _ in range(m)]
        dp[0][0][grid[0][0] % k] = 1
        for i in range(m):
            for j in range(n):
                for r in range(k):
                    ways = dp[i][j][r]
                    if not ways:
                        continue
                    if i + 1 < m:
                        nr = (r + grid[i + 1][j]) % k
                        dp[i + 1][j][nr] = (dp[i + 1][j][nr] + ways) % MOD
                    if j + 1 < n:
                        nr = (r + grid[i][j + 1]) % k
                        dp[i][j + 1][nr] = (dp[i][j + 1][nr] + ways) % MOD
        return dp[m - 1][n - 1][0]
# @lc code=end
