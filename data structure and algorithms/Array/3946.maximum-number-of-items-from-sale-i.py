#
# @lc app=leetcode id=3946 lang=python3
#
# [3946] Maximum Number of Items From Sale I
#
# https://leetcode.com/problems/maximum-number-of-items-from-sale-i/description/
#
# algorithms
# Medium (37.39%)
# Likes:    82
# Dislikes: 11
# Total Accepted:    21.3K
# Total Submissions: 57K
# Testcase Example:  "[[6,2],[2,6],[3,4]]\n9"
#
#
# You are given a 2D integer array items, where items[i] = [factor_i,
# price_i] represents the i^th item. You are also given an integer budget.
#
# There are unlimited copies of each item available for purchase.You may
# buy any number of copies of any items such that the total cost of the
# purchased copies is at most budget.
#
# After buying items, you may receive free copies according to the
# following rules:
#
# For each item i that you bought at least one copy of, you receive one
# free copy of every item j such that j != i and factor_i divides
# factor_j.
#
# Buying multiple copies of the same item i does not give additional free
# copies through item i.
#
# The same item j can be received multiple times for free if it is
# received from purchases of different item types.
#
# Return the maximum total number of item copies you can obtain, including
# both purchased copies and free copies, while spending at most budget on
# purchased items.
#
# Example 1:
#
# Input: items = [[6,2],[2,6],[3,4]], budget = 9
#
# Output: 4
#
# Explanation:
#
# You can buy 2 copies of item 0 and 1 copy of item 2 for a total cost of
# 2 * 2 + 4 = 8, which is not greater than budget = 9.
#
# Buying item 2 gives 1 free copy of item 0, because factor_2 = 3 divides
# factor_0 = 6.
#
# You leave with 3 purchased copies and 1 free copy, for a total of 4 item
# copies.
#
# Example 2:
#
# Input: items = [[2,4],[3,2],[4,1],[6,4],[12,4]], budget = 8
#
# Output: 10
#
# Explanation:
#
# You can buy 1 copy of item 0, 1 copy of item 1, and 2 copies of item 2
# for a total cost of 4 + 2 + 2 * 1 = 8.
#
# Buying item 0 gives 1 free copy of items 2, 3, and 4.
#
# Buying item 1 gives 1 free copy of items 3 and 4.
#
# Buying item 2 gives 1 free copy of item 4.
#
# Thus, you receive 6 free copies. You leave with 4 purchased copies and 6
# free copies, for a total of 10 item copies.
#
# Constraints:
#
# 1 <= items.length <= 1000
#
# items[i] = [factor_i, price_i]
#
# 1 <= factor_i, price_i <= 1500
#
# 1 <= budget <= 1500
#

# @lc code=start
from math import inf
from typing import List


class Solution:
    def maximumSaleItems(self, items: List[List[int]], budget: int) -> int:
        """
        Interview explanation:
        First copy of each type yields free multiples; extra copies are plain
        purchases. Model first copies as 0-1 knapsack, spend leftover on cheapest.

        Algorithm:
        - For each item, cnt = #items whose factor is a multiple (incl. itself).
        - 0-1 DP: buy first copy → +cnt items.
        - Answer max over spend i of f[i] + (budget-i)//min_price.

        Complexity: O(n² + n·budget) time, O(budget) space.
        """
        f = [0] * (budget + 1)
        mn = inf
        for factor, price in items:
            mn = min(mn, price)
            cnt = sum(fj % factor == 0 for fj, _ in items)
            for j in range(budget, price - 1, -1):
                f[j] = max(f[j], f[j - price] + cnt)
        return max(x + (budget - i) // mn for i, x in enumerate(f))
# @lc code=end
