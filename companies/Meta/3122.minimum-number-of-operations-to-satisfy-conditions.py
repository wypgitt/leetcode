#
# @lc app=leetcode id=3122 lang=python3
#
# [3122] Minimum Number of Operations to Satisfy Conditions
#
# https://leetcode.com/problems/minimum-number-of-operations-to-satisfy-conditions/description/
#
# algorithms
# Medium (42.49%)
# Likes:    303
# Dislikes: 14
# Total Accepted:    20.3K
# Total Submissions: 47.9K
# Testcase Example:  "[[1,0,2],[1,0,2]]"
#
#
# You are given a 2D matrix grid of size m x n. In one operation, you can
# change the value of any cell to any non-negative number. You need to
# perform some operations such that each cell grid[i][j] is:
#
# Equal to the cell below it, i.e. grid[i][j] == grid[i + 1][j] (if it
# exists).
#
# Different from the cell to its right, i.e. grid[i][j] != grid[i][j + 1]
# (if it exists).
#
# Return the minimum number of operations needed.
#
# Example 1:
#
# Input: grid = [[1,0,2],[1,0,2]]
#
# Output: 0
#
# Explanation:
#
# All the cells in the matrix already satisfy the properties.
#
# Example 2:
#
# Input: grid = [[1,1,1],[0,0,0]]
#
# Output: 3
#
# Explanation:
#
# The matrix becomes [[1,0,1],[1,0,1]] which satisfies the properties, by
# doing these 3 operations:
#
# Change grid[1][0] to 1.
#
# Change grid[0][1] to 0.
#
# Change grid[1][2] to 1.
#
# Example 3:
#
# Input: grid = [[1],[2],[3]]
#
# Output: 2
#
# Explanation:
#
# There is a single column. We can change the value to 1 in each cell
# using 2 operations.
#
# Constraints:
#
# 1 <= n, m <= 1000
#
# 0 <= grid[i][j] <= 9
#

# @lc code=start
from typing import List


class Solution:
    def minimumOperations(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Each column must be a constant value in 0..9, and adjacent columns must
        differ. Change any cell to any digit; minimize total changes.

        Algorithm:
        - Count digit frequencies per column.
        - DP over columns: dp[j][d] = min cost to paint column j as digit d,
          with previous column a different digit. Cost = m - freq[j][d].

        Complexity: O(m*n + n*10^2) time, O(10) space.
        """
        m, n = len(grid), len(grid[0])
        freq = [[0] * 10 for _ in range(n)]
        for j in range(n):
            for i in range(m):
                freq[j][grid[i][j]] += 1

        prev = [m - freq[0][d] for d in range(10)]
        for j in range(1, n):
            cur = [0] * 10
            for d in range(10):
                best = min(prev[pd] for pd in range(10) if pd != d)
                cur[d] = best + (m - freq[j][d])
            prev = cur
        return min(prev)

    def minimumOperations_full_dp(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Same column-constant / neighbor-different constraints; keep full DP table
        for clarity in interviews.

        Algorithm:
        - Build freq[j][d], then dp[j][d] from min over prev digits != d.

        Complexity: O(m*n + n*100) time, O(n*10) space.
        """
        m, n = len(grid), len(grid[0])
        freq = [[0] * 10 for _ in range(n)]
        for j in range(n):
            for i in range(m):
                freq[j][grid[i][j]] += 1
        INF = 10**18
        dp = [[INF] * 10 for _ in range(n)]
        for d in range(10):
            dp[0][d] = m - freq[0][d]
        for j in range(1, n):
            for d in range(10):
                dp[j][d] = min(dp[j - 1][pd] for pd in range(10) if pd != d) + (
                    m - freq[j][d]
                )
        return min(dp[-1])
# @lc code=end
