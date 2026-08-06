#
# @lc app=leetcode id=3693 lang=python3
#
# [3693] Climbing Stairs II
#
# https://leetcode.com/problems/climbing-stairs-ii/description/
#
# algorithms
# Medium (64.72%)
# Likes:    104
# Dislikes: 13
# Total Accepted:    35.6K
# Total Submissions: 55K
# Testcase Example:  "4\n[1,2,3,4]"
#
#
# You are climbing a staircase with n + 1 steps, numbered from 0 to n.
#
# You are also given a 1-indexed integer array costs of length n, where
# costs[i] is the cost of step i.
#
# From step i, you can jump only to step i + 1, i + 2, or i + 3. The cost
# of jumping from step i to step j is defined as: costs[j] + (j - i)^2
#
# You start from step 0 with cost = 0.
#
# Return the minimum total cost to reach step n.
#
# Example 1:
#
# Input: n = 4, costs = [1,2,3,4]
#
# Output: 13
#
# Explanation:
#
# One optimal path is 0 → 1 → 2 → 4
#
#                         Jump
#                         Cost Calculation
#                         Cost
#
#                         0 → 1
#                         costs[1] + (1 - 0)^2 = 1 + 1
#                         2
#
#                         1 → 2
#                         costs[2] + (2 - 1)^2 = 2 + 1
#                         3
#
#                         2 → 4
#                         costs[4] + (4 - 2)^2 = 4 + 4
#                         8
#
# Thus, the minimum total cost is 2 + 3 + 8 = 13
#
# Example 2:
#
# Input: n = 4, costs = [5,1,6,2]
#
# Output: 11
#
# Explanation:
#
# One optimal path is 0 → 2 → 4
#
#                         Jump
#                         Cost Calculation
#                         Cost
#
#                         0 → 2
#                         costs[2] + (2 - 0)^2 = 1 + 4
#                         5
#
#                         2 → 4
#                         costs[4] + (4 - 2)^2 = 2 + 4
#                         6
#
# Thus, the minimum total cost is 5 + 6 = 11
#
# Example 3:
#
# Input: n = 3, costs = [9,8,3]
#
# Output: 12
#
# Explanation:
#
# The optimal path is 0 → 3 with total cost = costs[3] + (3 - 0)^2 = 3 + 9
# = 12
#
# Constraints:
#
# 1 <= n == costs.length <= 10^5​​​​​​​
#
# 1 <= costs[i] <= 10^4
#

# @lc code=start

from typing import List


class Solution:
    def climbStairs(self, n: int, costs: List[int]) -> int:
        """
        Interview explanation:
        Classic jump DP: from i you may land on i+1..i+3, paying
        costs[j] + (j-i)^2 (0-based costs for step j).

        Algorithm:
        - dp[0] = 0; for each i, relax j in i+1..min(i+3,n).
        - Alternate: iterate landing step j and take min over j-1,j-2,j-3.

        Complexity: O(n) time, O(n) space (O(1) with rolling vars).
        """
        INF = 10**18
        dp = [0] + [INF] * n
        for i in range(n):
            for j in range(i + 1, min(i + 4, n + 1)):
                dp[j] = min(dp[j], dp[i] + costs[j - 1] + (j - i) * (j - i))
        return dp[n]
# @lc code=end
