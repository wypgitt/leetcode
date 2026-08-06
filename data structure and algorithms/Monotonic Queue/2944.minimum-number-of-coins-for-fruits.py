#
# @lc app=leetcode id=2944 lang=python3
#
# [2944] Minimum Number of Coins for Fruits
#
# https://leetcode.com/problems/minimum-number-of-coins-for-fruits/description/
#
# algorithms
# Medium (49.12%)
# Likes:    323
# Dislikes: 90
# Total Accepted:    25.3K
# Total Submissions: 51.5K
# Testcase Example:  "[3,1,2]"
#
#
# You are given an 0-indexed integer array prices where prices[i] denotes
# the number of coins needed to purchase the (i + 1)^th fruit.
#
# The fruit market has the following reward for each fruit:
#
# If you purchase the (i + 1)^th fruit at prices[i] coins, you can get any
# number of the next i fruits for free.
#
# Note that even if you can take fruit j for free, you can still purchase
# it for prices[j - 1] coins to receive its reward.
#
# Return the minimum number of coins needed to acquire all the fruits.
#
# Example 1:
#
# Input: prices = [3,1,2]
#
# Output: 4
#
# Explanation:
#
# Purchase the 1^st fruit with prices[0] = 3 coins, you are allowed to
# take the 2^nd fruit for free.
#
# Purchase the 2^nd fruit with prices[1] = 1 coin, you are allowed to take
# the 3^rd fruit for free.
#
# Take the 3^rd fruit for free.
#
# Note that even though you could take the 2^nd fruit for free as a reward
# of buying 1^st fruit, you purchase it to receive its reward, which is
# more optimal.
#
# Example 2:
#
# Input: prices = [1,10,1,1]
#
# Output: 2
#
# Explanation:
#
# Purchase the 1^st fruit with prices[0] = 1 coin, you are allowed to take
# the 2^nd fruit for free.
#
# Take the 2^nd fruit for free.
#
# Purchase the 3^rd fruit for prices[2] = 1 coin, you are allowed to take
# the 4^th fruit for free.
#
# Take the 4^t^h fruit for free.
#
# Example 3:
#
# Input: prices = [26,18,6,12,49,7,45,45]
#
# Output: 39
#
# Explanation:
#
# Purchase the 1^st fruit with prices[0] = 26 coin, you are allowed to
# take the 2^nd fruit for free.
#
# Take the 2^nd fruit for free.
#
# Purchase the 3^rd fruit for prices[2] = 6 coin, you are allowed to take
# the 4^th, 5^th and 6^th (the next three) fruits for free.
#
# Take the 4^t^h fruit for free.
#
# Take the 5^t^h fruit for free.
#
# Purchase the 6^th fruit with prices[5] = 7 coin, you are allowed to take
# the 8^th and 9^th fruit for free.
#
# Take the 7^t^h fruit for free.
#
# Take the 8^t^h fruit for free.
#
# Note that even though you could take the 6^th fruit for free as a reward
# of buying 3^rd fruit, you purchase it to receive its reward, which is
# more optimal.
#
# Constraints:
#
# 1 <= prices.length <= 1000
#
# 1 <= prices[i] <= 10^5
#

# @lc code=start
from typing import List
from functools import lru_cache


class Solution:
    def minimumCoins(self, prices: List[int]) -> int:
        """
        Interview explanation:
        Buying fruit i (0-index) costs prices[i] and grants the next (i+1)
        fruits free. Minimize coins to acquire all.

        Algorithm:
        - DP from the right: dp[i] = prices[i] + min(dp[j]) for next purchase
          j in (i, 2*i+2], with dp[n] = 0 when coverage reaches the end.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(prices)
        dp = [0] * (n + 1)
        for i in range(n - 1, -1, -1):
            end = min(n, 2 * i + 2)
            dp[i] = prices[i] + min(dp[j] for j in range(i + 1, end + 1))
        return dp[0]

    def minimumCoins_memo(self, prices: List[int]) -> int:
        """
        Interview explanation:
        Alternate top-down memoization of the same transitions.

        Algorithm:
        - Recurse on the leftmost unacquired index; try buying it.

        Complexity: O(n^2) time, O(n) space.
        """
        n = len(prices)

        @lru_cache(None)
        def dfs(i: int) -> int:
            if i >= n:
                return 0
            end = min(n, 2 * i + 2)
            return prices[i] + min(dfs(j) for j in range(i + 1, end + 1))

        return dfs(0)
# @lc code=end

