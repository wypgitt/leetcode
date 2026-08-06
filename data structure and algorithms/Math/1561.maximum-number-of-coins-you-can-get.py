#
# @lc app=leetcode id=1561 lang=python3
#
# [1561] Maximum Number of Coins You Can Get
#
# https://leetcode.com/problems/maximum-number-of-coins-you-can-get/description/
#
# algorithms
# Medium (84.83%)
# Likes:    1991
# Dislikes: 224
# Total Accepted:    206K
# Total Submissions: 243K
# Testcase Example:  "[2,4,1,2,7,8]"
#
# There are 3n piles of coins of varying size, you and your friends will take
# piles of coins as follows:
#
# In each step, you will choose any 3 piles of coins (not necessarily
# consecutive).
#
# Of your choice, Alice will pick the pile with the maximum number of coins.
#
# You will pick the next pile with the maximum number of coins.
#
# Your friend Bob will pick the last pile.
#
# Repeat until there are no more piles of coins.
#
# Given an array of integers piles where piles[i] is the number of coins in the
# i^th pile.
#
# Return the maximum number of coins that you can have.
#
# Example 1:
#
# Input: piles = [2,4,1,2,7,8]
# Output: 9
# Explanation: Choose the triplet (2, 7, 8), Alice Pick the pile with 8 coins,
# you the pile with 7 coins and Bob the last one.
# Choose the triplet (1, 2, 4), Alice Pick the pile with 4 coins, you the pile
# with 2 coins and Bob the last one.
# The maximum number of coins which you can have are: 7 + 2 = 9.
# On the other hand if we choose this arrangement (1, 2, 8), (2, 4, 7) you only
# get 2 + 4 = 6 coins which is not optimal.
#
# Example 2:
#
# Input: piles = [2,4,5]
# Output: 4
#
# Example 3:
#
# Input: piles = [9,8,7,6,5,1,2,3,4]
# Output: 18
#
# Constraints:
#
# 3 <= piles.length <= 10^5
#
# piles.length % 3 == 0
#
# 1 <= piles[i] <= 10^4
#

# @lc code=start
from typing import List


class Solution:
    def maxCoins(self, piles: List[int]) -> int:
        """
        Interview explanation:
        3n piles; each round Alice/you/Bob pick. Optimal: sort ascending; Bob
        always gets smallest leftover; Alice takes largest; you take second
        largest each round → sum every other from the high end, n times.

        Algorithm (sort):
        - piles.sort(); n=len//3; for i in 0..n-1: ans += piles[-(2*i+2)].

        Complexity: O(n log n) time, O(1)/O(n) space.
        """
        piles.sort()
        n = len(piles) // 3
        ans = 0
        # From the right: Alice, you, (Bob already took left n)
        idx = len(piles) - 2
        for _ in range(n):
            ans += piles[idx]
            idx -= 2
        return ans

    def maxCoins_slice(self, piles: List[int]) -> int:
        """
        Interview explanation:
        Alternate slice form: after sorting, Bob takes the smallest n piles;
        on the rest, Alice always takes the current max so you get every other
        starting at index n: sum(sorted(piles)[n:-1:2]).

        Algorithm:
        - n=len//3; return sum(sorted(piles)[n:-1:2])

        Complexity: O(n log n).
        """
        piles = sorted(piles)
        n = len(piles) // 3
        return sum(piles[n:-1:2])
# @lc code=end

