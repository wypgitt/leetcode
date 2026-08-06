#
# @lc app=leetcode id=2218 lang=python3
#
# [2218] Maximum Value of K Coins From Piles
#
# https://leetcode.com/problems/maximum-value-of-k-coins-from-piles/description/
#
# algorithms
# Hard (60.48%)
# Likes:    2471
# Dislikes: 39
# Total Accepted:    84.6K
# Total Submissions: 139.9K
# Testcase Example:  "[[1,100,3],[7,8,9]]\n2"
#
# There are n piles of coins on a table. Each pile consists of a positive number
# of coins of assorted denominations.
#
# In one move, you can choose any coin on top of any pile, remove it, and add it
# to your wallet.
#
# Given a list piles, where piles[i] is a list of integers denoting the
# composition of the i^th pile from top to bottom, and a positive integer k,
# return the maximum total value of coins you can have in your wallet if you
# choose exactly k coins optimally.
#
#
#
# Example 1:
#
# Input: piles = [[1,100,3],[7,8,9]], k = 2
# Output: 101
# Explanation:
# The above diagram shows the different ways we can choose k coins.
# The maximum total we can obtain is 101.
#
# Example 2:
#
# Input: piles = [[100],[100],[100],[100],[100],[100],[1,1,1,1,1,1,700]], k = 7
# Output: 706
# Explanation:
# The maximum total can be obtained if we choose all coins from the last pile.
#
#
#
# Constraints:
#
#
# n == piles.length
#
#
# 1 <= n <= 1000
#
#
# 1 <= piles[i][j] <= 10^5
#
#
# 1 <= k <= sum(piles[i].length) <= 2000
#

# @lc code=start
from typing import List


class Solution:
    def maxValueOfCoins(self, piles: List[List[int]], k: int) -> int:
        """
        Interview explanation:
        Piles are stacks; taking a coin requires taking all above it. Take exactly
        k coins total; maximize sum of values.

        Algorithm:
        (group knapsack DP)
        - dp[j]: max value using j coins from piles processed so far.
        - For each pile, try taking prefix of length t=0..min(k,len); update
          backwards.

        Complexity: O(k * total_coins) time, O(k) space.
        """
        dp = [0] + [0] * k
        for pile in piles:
            ndp = dp[:]
            pref = 0
            for t, v in enumerate(pile, 1):
                pref += v
                if t > k:
                    break
                for j in range(t, k + 1):
                    ndp[j] = max(ndp[j], dp[j - t] + pref)
            dp = ndp
        return dp[k]
# @lc code=end
