#
# @lc app=leetcode id=2561 lang=python3
#
# [2561] Rearranging Fruits
#
# https://leetcode.com/problems/rearranging-fruits/description/
#
# algorithms
# Hard (57.26%)
# Likes:    952
# Dislikes: 58
# Total Accepted:    99.3K
# Total Submissions: 173.4K
# Testcase Example:  "[4,2,2,2]\n[1,4,1,2]"
#
# You have two fruit baskets containing n fruits each. You are given two
# 0-indexed integer arrays basket1 and basket2 representing the cost of fruit in
# each basket. You want to make both baskets equal. To do so, you can use the
# following operation as many times as you want:
#
#
# Choose two indices i and j, and swap the i^th fruit of basket1 with the j^th
# fruit of basket2.
#
#
# The cost of the swap is min(basket1[i], basket2[j]).
#
# Two baskets are considered equal if sorting them according to the fruit cost
# makes them exactly the same baskets.
#
# Return the minimum cost to make both the baskets equal or -1 if impossible.
#
#
#
# Example 1:
#
# Input: basket1 = [4,2,2,2], basket2 = [1,4,1,2]
# Output: 1
# Explanation: Swap index 1 of basket1 with index 0 of basket2, which has cost
# 1. Now basket1 = [4,1,2,2] and basket2 = [2,4,1,2]. Rearranging both the
# arrays makes them equal.
#
# Example 2:
#
# Input: basket1 = [2,3,4,1], basket2 = [3,2,5,1]
# Output: -1
# Explanation: It can be shown that it is impossible to make both the baskets
# equal.
#
#
#
# Constraints:
#
#
# basket1.length == basket2.length
#
#
# 1 <= basket1.length <= 10^5
#
#
# 1 <= basket1[i], basket2[i] <= 10^9
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def minCost(self, basket1: List[int], basket2: List[int]) -> int:
        """
        Interview explanation:
        Make two baskets equal by swapping fruits. Cost of a swap is min of the two
        swapped values. Use the global minimum as a double-swap relay when cheaper.

        Algorithm:
        - Count net imbalance; odd counts => impossible (-1).
        - Collect excess values to swap (half of each imbalance); sort.
        - Pair cheapest from left with dearest from right; cost min(v, 2*global_min).

        Complexity: O(n log n) time, O(n) space.
        """
        cnt = Counter(basket1)
        for x in basket2:
            cnt[x] -= 1
        swap = []
        for v, c in cnt.items():
            if c % 2:
                return -1
            swap.extend([v] * (abs(c) // 2))
        if not swap:
            return 0
        swap.sort()
        mn = min(min(basket1), min(basket2))
        m = len(swap) // 2
        return sum(min(swap[i], 2 * mn) for i in range(m))
# @lc code=end
