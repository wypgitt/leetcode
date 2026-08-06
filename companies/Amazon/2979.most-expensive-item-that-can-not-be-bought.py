#
# @lc app=leetcode id=2979 lang=python3
#
# [2979] Most Expensive Item That Can Not Be Bought
#
# https://leetcode.com/problems/most-expensive-item-that-can-not-be-bought/description/
#
# algorithms
# Medium (80.16%)
# Likes:    25
# Dislikes: 28
# Total Accepted:    6.6K
# Total Submissions: 8.2K
# Testcase Example:  "2\n5"
#
#
# You are given two distinct prime numbers primeOne and primeTwo.
#
# Alice and Bob are visiting a market. The market has an infinite number
# of items, for any positive integer x there exists an item whose price is
# x. Alice wants to buy some items from the market to gift to Bob. She has
# an infinite number of coins in the denomination primeOne and primeTwo.
# She wants to know the most expensive item she can not buy to gift to
# Bob.
#
# Return the price of the most expensive item which Alice can not gift to
# Bob.
#
# Example 1:
#
# Input: primeOne = 2, primeTwo = 5
# Output: 3
# Explanation: The prices of items which cannot be bought are [1,3]. It
# can be shown that all items with a price greater than 3 can be bought
# using a combination of coins of denominations 2 and 5.
#
# Example 2:
#
# Input: primeOne = 5, primeTwo = 7
# Output: 23
# Explanation: The prices of items which cannot be bought are
# [1,2,3,4,6,8,9,11,13,16,18,23]. It can be shown that all items with a
# price greater than 23 can be bought.
#
# Constraints:
#
# 1 < primeOne, primeTwo < 10^4
#
# primeOne, primeTwo are prime numbers.
#
# primeOne * primeTwo < 10^5
#
# @lc code=start

class Solution:
    def mostExpensiveItem(self, primeOne: int, primeTwo: int) -> int:
        """
        Interview explanation:
        Premium: unlimited coins of two distinct primes; largest price that cannot be
        formed as non-negative combination (Frobenius / Chicken McNugget).

        Algorithm:
        - For coprime a,b the answer is ab - a - b. Distinct primes ⇒ coprime.

        Complexity: O(1) time, O(1) space.
        """
        return primeOne * primeTwo - primeOne - primeTwo
# @lc code=end
