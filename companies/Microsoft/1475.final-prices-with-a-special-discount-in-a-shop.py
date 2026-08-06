#
# @lc app=leetcode id=1475 lang=python3
#
# [1475] Final Prices With a Special Discount in a Shop
#
# https://leetcode.com/problems/final-prices-with-a-special-discount-in-a-shop/description/
#
# algorithms
# Easy (84.28%)
# Likes:    2979
# Dislikes: 157
# Total Accepted:    442K
# Total Submissions: 524K
# Testcase Example:  "[8,4,6,2,3]"
#
# You are given an integer array prices where prices[i] is the price of the
# i^th item in a shop.
#
# There is a special discount for items in the shop. If you buy the i^th item,
# then you will receive a discount equivalent to prices[j] where j is the
# minimum index such that j > i and prices[j] <= prices[i]. Otherwise, you will
# not receive any discount at all.
#
# Return an integer array answer where answer[i] is the final price you will
# pay for the i^th item of the shop, considering the special discount.
#
# Example 1:
#
# Input: prices = [8,4,6,2,3]
# Output: [4,2,4,2,3]
# Explanation:
# For item 0 with price[0]=8 you will receive a discount equivalent to
# prices[1]=4, therefore, the final price you will pay is 8 - 4 = 4.
# For item 1 with price[1]=4 you will receive a discount equivalent to
# prices[3]=2, therefore, the final price you will pay is 4 - 2 = 2.
# For item 2 with price[2]=6 you will receive a discount equivalent to
# prices[3]=2, therefore, the final price you will pay is 6 - 2 = 4.
# For items 3 and 4 you will not receive any discount at all.
#
# Example 2:
#
# Input: prices = [1,2,3,4,5]
# Output: [1,2,3,4,5]
# Explanation: In this case, for all items, you will not receive any discount
# at all.
#
# Example 3:
#
# Input: prices = [10,1,1,6]
# Output: [9,0,1,6]
#
# Constraints:
#
# 1 <= prices.length <= 500
#
# 1 <= prices[i] <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def finalPrices(self, prices: List[int]) -> List[int]:
        """
        Interview explanation:
        Discount = next smaller-or-equal price to the right (next non-greater).
        Monotonic non-decreasing stack of indices.

        Algorithm:
        - Stack increasing; while stack and prices[stack.top] >= prices[i],
          pop and apply discount; push i. Unpopped keep full price.

        Complexity: O(n) time, O(n) space.
        """
        n = len(prices)
        ans = prices[:]
        stack = []
        for i, p in enumerate(prices):
            while stack and prices[stack[-1]] >= p:
                j = stack.pop()
                ans[j] = prices[j] - p
            stack.append(i)
        return ans

    def finalPrices_brute(self, prices: List[int]) -> List[int]:
        """
        Interview explanation:
        Alternate: for each i scan right for first j with prices[j] <= prices[i].

        Algorithm:
        - Nested loops; apply discount when found.

        Complexity: O(n^2) time, O(n) space for answer.
        """
        n = len(prices)
        ans = prices[:]
        for i in range(n):
            for j in range(i + 1, n):
                if prices[j] <= prices[i]:
                    ans[i] = prices[i] - prices[j]
                    break
        return ans
# @lc code=end
