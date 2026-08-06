#
# @lc app=leetcode id=3603 lang=python3
#
# [3603] Minimum Cost Path with Alternating Directions II
#
# https://leetcode.com/problems/minimum-cost-path-with-alternating-directions-ii/description/
#
# algorithms
# Medium (45.29%)
# Likes:    76
# Dislikes: 13
# Total Accepted:    20K
# Total Submissions: 44.3K
# Testcase Example:  "1\n2\n[[1,2]]"
#
#
# You are given two integers m and n representing the number of rows and
# columns of a grid, respectively.
#
# The cost to enter cell (i, j) is defined as (i + 1) * (j + 1).
#
# You are also given a 2D integer array waitCost where waitCost[i][j]
# defines the cost to wait on that cell.
#
# The path will always begin by entering cell (0, 0) on move 1 and paying
# the entrance cost.
#
# At each step, you follow an alternating pattern:
#
# On odd-numbered seconds, you must move right or down to an adjacent
# cell, paying its entry cost.
#
# On even-numbered seconds, you must wait in place for exactly one second
# and pay waitCost[i][j] during that second.
#
# Return the minimum total cost required to reach (m - 1, n - 1).
#
# Example 1:
#
# Input: m = 1, n = 2, waitCost = [[1,2]]
#
# Output: 3
#
# Explanation:
#
# The optimal path is:
#
# Start at cell (0, 0) at second 1 with entry cost (0 + 1) * (0 + 1) = 1.
#
# Second 1: Move right to cell (0, 1) with entry cost (0 + 1) * (1 + 1) =
# 2.
#
# Thus, the total cost is 1 + 2 = 3.
#
# Example 2:
#
# Input: m = 2, n = 2, waitCost = [[3,5],[2,4]]
#
# Output: 9
#
# Explanation:
#
# The optimal path is:
#
# Start at cell (0, 0) at second 1 with entry cost (0 + 1) * (0 + 1) = 1.
#
# Second 1: Move down to cell (1, 0) with entry cost (1 + 1) * (0 + 1) =
# 2.
#
# Second 2: Wait at cell (1, 0), paying waitCost[1][0] = 2.
#
# Second 3: Move right to cell (1, 1) with entry cost (1 + 1) * (1 + 1) =
# 4.
#
# Thus, the total cost is 1 + 2 + 2 + 4 = 9.
#
# Example 3:
#
# Input: m = 2, n = 3, waitCost = [[6,1,4],[3,2,5]]
#
# Output: 16
#
# Explanation:
#
# The optimal path is:
#
# Start at cell (0, 0) at second 1 with entry cost (0 + 1) * (0 + 1) = 1.
#
# Second 1: Move right to cell (0, 1) with entry cost (0 + 1) * (1 + 1) =
# 2.
#
# Second 2: Wait at cell (0, 1), paying waitCost[0][1] = 1.
#
# Second 3: Move down to cell (1, 1) with entry cost (1 + 1) * (1 + 1) =
# 4.
#
# Second 4: Wait at cell (1, 1), paying waitCost[1][1] = 2.
#
# Second 5: Move right to cell (1, 2) with entry cost (1 + 1) * (2 + 1) =
# 6.
#
# Thus, the total cost is 1 + 2 + 1 + 4 + 2 + 6 = 16.
#
# Constraints:
#
# 1 <= m, n <= 10^5
#
# 2 <= m * n <= 10^5
#
# waitCost.length == m
#
# waitCost[0].length == n
#
# 0 <= waitCost[i][j] <= 10^5
#

# @lc code=start

from typing import List


class Solution:
    def minCost(self, m: int, n: int, waitCost: List[List[int]]) -> int:
        """
        Interview explanation:
        Only right/down moves on odd seconds; even seconds force a wait.
        Wait is paid on every cell except start and destination.

        Algorithm:
        - Zero waitCost at start and end.
        - DP[i][j] = entry(i,j) + wait(i,j) + min(DP from up/left).
        - Start contributes only its entry cost.

        Complexity: O(m*n) time, O(n) space with rolling DP.
        """
        waitCost[0][0] = 0
        waitCost[m - 1][n - 1] = 0
        dp = [0] * n
        for i in range(m):
            for j in range(n):
                prev = 0 if (i, j) == (0, 0) else float("inf")
                if i - 1 >= 0:
                    prev = min(prev, dp[j])
                if j - 1 >= 0:
                    prev = min(prev, dp[j - 1])
                dp[j] = prev + waitCost[i][j] + (i + 1) * (j + 1)
        return int(dp[n - 1])

    def minCost_inplace(self, m: int, n: int, waitCost: List[List[int]]) -> int:
        """
        Interview explanation:
        Alternate in-place DP mutating waitCost as the cost grid.

        Algorithm:
        - Same recurrence; store answers directly in waitCost.

        Complexity: O(m*n) time, O(1) extra space.
        """
        waitCost[0][0] = 0
        waitCost[m - 1][n - 1] = 0
        for i in range(m):
            for j in range(n):
                prev = 0 if (i, j) == (0, 0) else float("inf")
                if i - 1 >= 0:
                    prev = min(prev, waitCost[i - 1][j])
                if j - 1 >= 0:
                    prev = min(prev, waitCost[i][j - 1])
                waitCost[i][j] += prev + (i + 1) * (j + 1)
        return int(waitCost[m - 1][n - 1])
# @lc code=end
