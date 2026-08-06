#
# @lc app=leetcode id=3947 lang=python3
#
# [3947] Maximum Number of Items From Sale II
#
# https://leetcode.com/problems/maximum-number-of-items-from-sale-ii/description/
#
# algorithms
# Medium (31.05%)
# Likes:    48
# Dislikes: 9
# Total Accepted:    6.8K
# Total Submissions: 21.8K
# Testcase Example:  "[[1,6],[2,4],[3,5]]\n19"
#
#
# You are given a 2D integer array items, where items[i] = [factor_i,
# price_i] represents the i^th item. You are also given an integer budget.
#
# There are unlimited copies of each item available for purchase. You may
# buy any number of copies of any items such that the total cost of the
# purchased copies is at most budget.
#
# After buying items, you may receive free copies according to the
# following rules:
#
# Each purchased copy of item i can give you at most one free copy of
# another item j.
#
# The free item must satisfy i != j and factor_i divides factor_j.
#
# For each ordered pair (i, j), you can receive a free copy of item j from
# purchases of item i at most once, regardless of how many copies of item
# i you buy.
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
# Input: items = [[1,6],[2,4],[3,5]], budget = 19
#
# Output: 5
#
# Explanation:
#
# You can buy 2 copies of item 0 and 1 copy of item 1 for a total cost of
# 2 * 6 + 4 = 16, which is not greater than budget = 19.
#
# One purchased copy of item 0 gives 1 free copy of item 1, because
# factor_0 = 1 divides factor_1 = 2.
#
# The other purchased copy of item 0 gives 1 free copy of item 2, because
# factor_0 = 1 divides factor_2 = 3.
#
# You leave with 3 purchased copies and 2 free copies, for a total of 5
# item copies.
#
# Example 2:
#
# Input: items = [[2,8],[1,10],[6,6],[4,12],[5,20],[5,17]], budget = 35
#
# Output: 7
#
# Explanation:
#
# You can buy 2 copies of item 0, 1 copy of item 1, and 1 copy of item 2
# for a total cost of 2 * 8 + 10 + 6 = 32, which is not greater than
# budget = 35.
#
# One purchased copy of item 0 gives 1 free copy of item 2, because
# factor_0 = 2 divides factor_2 = 6.
#
# The other purchased copy of item 0 gives 1 free copy of item 3, because
# factor_0 = 2 divides factor_3 = 4.
#
# The purchased copy of item 1 gives 1 free copy of item 2, because
# factor_1 = 1 divides factor_2 = 6.
#
# Buying item 2 gives no free copy, because factor_2 = 6 does not divide
# the factor of any other item.
#
# You leave with 4 purchased copies and 3 free copies, for a total of 7
# item copies.
#
# Constraints:
#
# 1 <= items.length <= 10^5
#
# items[i] = [factor_i, price_i]
#
# 1 <= factor_i <= items.length
#
# 1 <= price_i <= 10^9
#
# 1 <= budget <= 10^9
#

# @lc code=start
from collections import defaultdict
from typing import List


class Solution:
    def maximumSaleItems(self, items: List[List[int]], budget: int) -> int:
        """
        Interview explanation:
        Buying c copies of type i yields c + min(c, gain[i]) items. Value-2
        marginal units (bonus pairs) should be bought cheapest-first; leftovers
        go to the global cheapest item as value-1 units.

        Algorithm:
        - Sieve multiples to get gain[factor] = (#multiples) - 1.
        - Collect bonus slots with price ≤ 2·min_price; sort by price.
        - Greedily take bonus pairs, then spend remainder on min price.

        Complexity: O(n log n + F log F) time, O(n) space.
        """
        cheapest = min(p for _, p in items)
        max_factor = max(f for f, _ in items)
        freq = [0] * (max_factor + 1)
        for f, _ in items:
            freq[f] += 1
        for i in range(1, max_factor + 1):
            if freq[i]:
                for mult in range(2 * i, max_factor + 1, i):
                    freq[i] += freq[mult]

        cost_count = defaultdict(int)
        for f, cost in items:
            cnt = freq[f] - 1
            if cnt > 0 and cost <= 2 * cheapest:
                cost_count[cost] += cnt

        total = 0
        for cost in sorted(cost_count):
            cnt = cost_count[cost]
            take = min(cnt, budget // cost)
            total += 2 * take
            budget -= take * cost
        total += budget // cheapest
        return total
# @lc code=end
