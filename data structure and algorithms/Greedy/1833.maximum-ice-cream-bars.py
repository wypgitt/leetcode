#
# @lc app=leetcode id=1833 lang=python3
#
# [1833] Maximum Ice Cream Bars
#
# https://leetcode.com/problems/maximum-ice-cream-bars/description/
#
# algorithms
# Medium (77.24%)
# Likes:    2504
# Dislikes: 689
# Total Accepted:    341K
# Total Submissions: 441K
# Testcase Example:  "[1,3,2,4,1]"
#
# It is a sweltering summer day, and a boy wants to buy some ice cream bars.
#
# At the store, there are n ice cream bars. You are given an array costs of
# length n, where costs[i] is the price of the i^th ice cream bar in coins. The
# boy initially has coins coins to spend, and he wants to buy as many ice cream
# bars as possible.
#
# Note: The boy can buy the ice cream bars in any order.
#
# Return the maximum number of ice cream bars the boy can buy with coins coins.
#
# You must solve the problem by counting sort.
#
# Example 1:
#
# Input: costs = [1,3,2,4,1], coins = 7
# Output: 4
# Explanation: The boy can buy ice cream bars at indices 0,1,2,4 for a total
# price of 1 + 3 + 2 + 1 = 7.
#
# Example 2:
#
# Input: costs = [10,6,8,7,7,8], coins = 5
# Output: 0
# Explanation: The boy cannot afford any of the ice cream bars.
#
# Example 3:
#
# Input: costs = [1,6,3,1,2,5], coins = 20
# Output: 6
# Explanation: The boy can buy all the ice cream bars for a total price of 1 +
# 6 + 3 + 1 + 2 + 5 = 18.
#
# Constraints:
#
# costs.length == n
#
# 1 <= n <= 10^5
#
# 1 <= costs[i] <= 10^5
#
# 1 <= coins <= 10^8
#

# @lc code=start
from typing import List


class Solution:
    def maxIceCream(self, costs: List[int], coins: int) -> int:
        """
        Interview explanation:
        Buy as many bars as possible; greedily take cheapest first.

        Algorithm (sort greedy):
        - Sort costs; buy while coins allow.

        Complexity: O(n log n) time, O(1)/O(n) space.
        """
        costs.sort()
        ans = 0
        for c in costs:
            if coins < c:
                break
            coins -= c
            ans += 1
        return ans

    def maxIceCream_counting(self, costs: List[int], coins: int) -> int:
        """
        Interview explanation:
        Alternate counting sort when costs are small (up to 1e5).

        Algorithm (counting):
        - freq[cost]++; scan costs ascending spending coins.

        Complexity: O(n + C) time, O(C) space.
        """
        mx = max(costs)
        freq = [0] * (mx + 1)
        for c in costs:
            freq[c] += 1
        ans = 0
        for c in range(1, mx + 1):
            if not freq[c]:
                continue
            can = min(freq[c], coins // c)
            ans += can
            coins -= can * c
            if coins < c:
                break
        return ans
# @lc code=end
