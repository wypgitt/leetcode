#
# @lc app=leetcode id=1774 lang=python3
#
# [1774] Closest Dessert Cost
#
# https://leetcode.com/problems/closest-dessert-cost/description/
#
# algorithms
# Medium (48.85%)
# Likes:    744
# Dislikes: 95
# Total Accepted:    40.2K
# Total Submissions: 82.3K
# Testcase Example:  "[1,7]"
#
# You would like to make dessert and are preparing to buy the ingredients. You
# have n ice cream base flavors and m types of toppings to choose from. You
# must follow these rules when making your dessert:
#
# There must be exactly one ice cream base.
#
# You can add one or more types of topping or have no toppings at all.
#
# There are at most two of each type of topping.
#
# You are given three inputs:
#
# baseCosts, an integer array of length n, where each baseCosts[i] represents
# the price of the i^th ice cream base flavor.
#
# toppingCosts, an integer array of length m, where each toppingCosts[i] is the
# price of one of the i^th topping.
#
# target, an integer representing your target price for dessert.
#
# You want to make a dessert with a total cost as close to target as possible.
#
# Return the closest possible cost of the dessert to target. If there are
# multiple, return the lower one.
#
# Example 1:
#
# Input: baseCosts = [1,7], toppingCosts = [3,4], target = 10
# Output: 10
# Explanation: Consider the following combination (all 0-indexed):
# - Choose base 1: cost 7
# - Take 1 of topping 0: cost 1 x 3 = 3
# - Take 0 of topping 1: cost 0 x 4 = 0
# Total: 7 + 3 + 0 = 10.
#
# Example 2:
#
# Input: baseCosts = [2,3], toppingCosts = [4,5,100], target = 18
# Output: 17
# Explanation: Consider the following combination (all 0-indexed):
# - Choose base 1: cost 3
# - Take 1 of topping 0: cost 1 x 4 = 4
# - Take 2 of topping 1: cost 2 x 5 = 10
# - Take 0 of topping 2: cost 0 x 100 = 0
# Total: 3 + 4 + 10 + 0 = 17. You cannot make a dessert with a total cost of
# 18.
#
# Example 3:
#
# Input: baseCosts = [3,10], toppingCosts = [2,5], target = 9
# Output: 8
# Explanation: It is possible to make desserts with cost 8 and 10. Return 8 as
# it is the lower cost.
#
# Constraints:
#
# n == baseCosts.length
#
# m == toppingCosts.length
#
# 1 <= n, m <= 10
#
# 1 <= baseCosts[i], toppingCosts[i] <= 10^4
#
# 1 <= target <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def closestCost(self, baseCosts: List[int], toppingCosts: List[int], target: int) -> int:
        """
        Interview explanation:
        Pick one base; each topping 0/1/2 times. Enumerate all topping sums via
        DFS/backtracking (m≤10 → 3^m≤59049); for each base find sum closest to
        target (prefer lower on ties).

        Algorithm:
        - DFS generate all topping totals into a set.
        - For each base+top: track best by |cost-target|, then smaller cost.

        Complexity: O(3^m * B) time, O(3^m) space.
        """
        tops = set([0])

        def dfs(i: int, cur: int) -> None:
            if i == len(toppingCosts):
                tops.add(cur)
                return
            dfs(i + 1, cur)
            dfs(i + 1, cur + toppingCosts[i])
            dfs(i + 1, cur + 2 * toppingCosts[i])

        dfs(0, 0)
        best = float("inf")
        for b in baseCosts:
            for t in tops:
                cost = b + t
                if abs(cost - target) < abs(best - target) or (
                    abs(cost - target) == abs(best - target) and cost < best
                ):
                    best = cost
        return best

    def closestCost_iter(self, baseCosts: List[int], toppingCosts: List[int], target: int) -> int:
        """
        Interview explanation:
        Alternate iterative expand of topping sums (same 0/1/2 choices).

        Algorithm:
        - Start sums={0}; for each topping, expand with +0,+x,+2x.

        Complexity: O(3^m * B).
        """
        sums = {0}
        for x in toppingCosts:
            sums = {s + k * x for s in sums for k in (0, 1, 2)}
        best = float("inf")
        for b in baseCosts:
            for t in sums:
                cost = b + t
                if abs(cost - target) < abs(best - target) or (
                    abs(cost - target) == abs(best - target) and cost < best
                ):
                    best = cost
        return best
# @lc code=end
