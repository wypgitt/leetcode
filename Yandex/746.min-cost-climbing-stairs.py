#
# @lc app=leetcode id=746 lang=python3
#
# [746] Min Cost Climbing Stairs
#
# https://leetcode.com/problems/min-cost-climbing-stairs/description/
#
# algorithms
# Easy (68.59%)
# Likes:    12481
# Dislikes: 1905
# Total Accepted:    1.8M
# Total Submissions: 2.7M
# Testcase Example:  "[10,15,20]"
#
# You are given an integer array cost where cost[i] is the cost of i^th step on
# a staircase. Once you pay the cost, you can either climb one or two steps.
#
# You can either start from the step with index 0, or the step with index 1.
#
# Return the minimum cost to reach the top of the floor.
#
# Example 1:
#
# Input: cost = [10,15,20]
# Output: 15
# Explanation: You will start at index 1.
# - Pay 15 and climb two steps to reach the top.
# The total cost is 15.
#
# Example 2:
#
# Input: cost = [1,100,1,1,1,100,1,1,100,1]
# Output: 6
# Explanation: You will start at index 0.
# - Pay 1 and climb two steps to reach index 2.
# - Pay 1 and climb two steps to reach index 4.
# - Pay 1 and climb two steps to reach index 6.
# - Pay 1 and climb one step to reach index 7.
# - Pay 1 and climb two steps to reach index 9.
# - Pay 1 and climb one step to reach the top.
# The total cost is 6.
#
# Constraints:
#
# 2 <= cost.length <= 1000
#
# 0 <= cost[i] <= 999
#


# @lc code=start
from typing import List


class Solution:
    def minCostClimbingStairs(self, cost: List[int]) -> int:
        """
        Interview explanation:
        You may start at step 0 or 1; from i pay cost[i] and jump +1 or +2.
        DP: min cost to reach top from i is cost[i] + min(from i+1, from i+2).
        Rolling two variables bottom-up from the end (or from the start).

        Algorithm:
        - a = b = 0  # min cost after processing from the top
        - For c in reversed(cost): a, b = c + min(a, b), a
        - Return min(a, b)  # start at 0 or 1

        Complexity: O(n) time, O(1) space.
        """
        a = b = 0
        for c in reversed(cost):
            a, b = c + min(a, b), a
        return min(a, b)
# @lc code=end

