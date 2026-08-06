#
# @lc app=leetcode id=1289 lang=python3
#
# [1289] Minimum Falling Path Sum II
#
# https://leetcode.com/problems/minimum-falling-path-sum-ii/description/
#
# algorithms
# Hard (62.99%)
# Likes:    2397
# Dislikes: 124
# Total Accepted:    169K
# Total Submissions: 269K
# Testcase Example:  "[[1,2,3],[4,5,6],[7,8,9]]"
#
# Given an n x n integer matrix grid, return the minimum sum of a falling path
# with non-zero shifts.
#
# A falling path with non-zero shifts is a choice of exactly one element from
# each row of grid such that no two elements chosen in adjacent rows are in the
# same column.
#
# Example 1:
#
# Input: grid = [[1,2,3],[4,5,6],[7,8,9]]
# Output: 13
# Explanation:
# The possible falling paths are:
# [1,5,9], [1,5,7], [1,6,7], [1,6,8],
# [2,4,8], [2,4,9], [2,6,7], [2,6,8],
# [3,4,8], [3,4,9], [3,5,7], [3,5,9]
# The falling path with the smallest sum is [1,5,7], so the answer is 13.
#
# Example 2:
#
# Input: grid = [[7]]
# Output: 7
#
# Constraints:
#
# n == grid.length == grid[i].length
#
# 1 <= n <= 200
#
# -99 <= grid[i][j] <= 99
#

# @lc code=start

from typing import List


class Solution:
    def minFallingPathSum(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Falling path with no two in same column consecutively. For each row
        keep the two smallest values from previous row so choosing any column
        avoids the previous column of the min in O(1).

        Algorithm:
        - Track (min1, i1), (min2, i2) of previous row.
        - For each cell j: use min1 if j!=i1 else min2; add grid[r][j].
        - Update two mins for next row.

        Complexity: O(n^2) time, O(1) extra space.
        """
        n = len(grid)
        INF = 10**18
        prev = grid[0][:]
        for r in range(1, n):
            # two smallest in prev
            m1 = m2 = INF
            i1 = -1
            for j, v in enumerate(prev):
                if v < m1:
                    m2, m1 = m1, v
                    i1 = j
                elif v < m2:
                    m2 = v
            cur = [0] * n
            for j in range(n):
                cur[j] = grid[r][j] + (m2 if j == i1 else m1)
            prev = cur
        return min(prev)

    def minFallingPathSum_dp(self, grid: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate classic DP: dp[j]=grid[r][j]+min(dp[k] for k!=j).

        Algorithm:
        - Each row recompute with O(n) min scan avoiding same column.

        Complexity: O(n^3) naive or O(n^2) with two-mins (same as primary).
        """
        n = len(grid)
        dp = grid[0][:]
        for r in range(1, n):
            ndp = [0] * n
            for j in range(n):
                ndp[j] = grid[r][j] + min(dp[k] for k in range(n) if k != j)
            dp = ndp
        return min(dp)
# @lc code=end
