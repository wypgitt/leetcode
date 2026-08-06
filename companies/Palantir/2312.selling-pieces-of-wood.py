#
# @lc app=leetcode id=2312 lang=python3
#
# [2312] Selling Pieces of Wood
#
# https://leetcode.com/problems/selling-pieces-of-wood/description/
#
# algorithms
# Hard (53.14%)
# Likes:    581
# Dislikes: 13
# Total Accepted:    16.3K
# Total Submissions: 30.7K
# Testcase Example:  "3\n5\n[[1,4,2],[2,2,7],[2,1,3]]"
#
# You are given two integers m and n that represent the height and width of a
# rectangular piece of wood. You are also given a 2D integer array prices, where
# prices[i] = [h_i, w_i, price_i] indicates you can sell a rectangular piece of
# wood of height h_i and width w_i for price_i dollars.
#
# To cut a piece of wood, you must make a vertical or horizontal cut across the
# entire height or width of the piece to split it into two smaller pieces. After
# cutting a piece of wood into some number of smaller pieces, you can sell
# pieces according to prices. You may sell multiple pieces of the same shape,
# and you do not have to sell all the shapes. The grain of the wood makes a
# difference, so you cannot rotate a piece to swap its height and width.
#
# Return the maximum money you can earn after cutting an m x n piece of wood.
#
# Note that you can cut the piece of wood as many times as you want.
#
#
#
# Example 1:
#
# Input: m = 3, n = 5, prices = [[1,4,2],[2,2,7],[2,1,3]]
# Output: 19
# Explanation: The diagram above shows a possible scenario. It consists of:
# - 2 pieces of wood shaped 2 x 2, selling for a price of 2 * 7 = 14.
# - 1 piece of wood shaped 2 x 1, selling for a price of 1 * 3 = 3.
# - 1 piece of wood shaped 1 x 4, selling for a price of 1 * 2 = 2.
# This obtains a total of 14 + 3 + 2 = 19 money earned.
# It can be shown that 19 is the maximum amount of money that can be earned.
#
# Example 2:
#
# Input: m = 4, n = 6, prices = [[3,2,10],[1,4,2],[4,1,3]]
# Output: 32
# Explanation: The diagram above shows a possible scenario. It consists of:
# - 3 pieces of wood shaped 3 x 2, selling for a price of 3 * 10 = 30.
# - 1 piece of wood shaped 1 x 4, selling for a price of 1 * 2 = 2.
# This obtains a total of 30 + 2 = 32 money earned.
# It can be shown that 32 is the maximum amount of money that can be earned.
# Notice that we cannot rotate the 1 x 4 piece of wood to obtain a 4 x 1 piece
# of wood.
#
#
#
# Constraints:
#
#
# 1 <= m, n <= 200
#
#
# 1 <= prices.length <= 2 * 10^4
#
#
# prices[i].length == 3
#
#
# 1 <= h_i <= m
#
#
# 1 <= w_i <= n
#
#
# 1 <= price_i <= 10^6
#
#
# All the shapes of wood (h_i, w_i) are pairwise distinct.
#

# @lc code=start
from typing import List


class Solution:
    def sellingWood(self, m: int, n: int, prices: List[List[int]]) -> int:
        """
        Interview explanation:
        Cut an m x n board (horizontal/vertical through cuts) to maximize
        revenue from given piece prices (h,w,price). Unused scraps worth 0.

        Algorithm:
        - DP: dp[h][w] = max money for h x w board.
        - Initialize with direct prices; try all horizontal/vertical cuts.

        Complexity: O(m*n*(m+n) + |prices|) time, O(m*n) space.
        """
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for h, w, p in prices:
            dp[h][w] = max(dp[h][w], p)
        for h in range(1, m + 1):
            for w in range(1, n + 1):
                for x in range(1, h // 2 + 1):
                    dp[h][w] = max(dp[h][w], dp[x][w] + dp[h - x][w])
                for y in range(1, w // 2 + 1):
                    dp[h][w] = max(dp[h][w], dp[h][y] + dp[h][w - y])
        return dp[m][n]

    def sellingWood_dp(self, m: int, n: int, prices: List[List[int]]) -> int:
        """
        Interview explanation:
        Classic 2D cutting DP (same as primary).

        Algorithm:
        - Enumerate cut positions for every sub-rectangle.

        Complexity: O(m*n*(m+n)) time, O(m*n) space.
        """
        return self.sellingWood(m, n, prices)
# @lc code=end
