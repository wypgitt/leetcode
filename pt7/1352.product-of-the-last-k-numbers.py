#
# @lc app=leetcode id=1352 lang=python3
#
# [1352] Product of the Last K Numbers
#
# https://leetcode.com/problems/product-of-the-last-k-numbers/description/
#
# algorithms
# Medium (62.92%)
# Likes:    2171
# Dislikes: 110
# Total Accepted:    262.5K
# Total Submissions: 417.3K
# Testcase Example:  '["ProductOfNumbers","add","add","add","add","add","getProduct","getProduct","getProduct","add","getProduct"]\n' +
# '[[],[3],[0],[2],[5],[4],[2],[3],[4],[8],[2]]'
#
# Design an algorithm that accepts a stream of integers and retrieves the
# product of the last k integers of the stream.
# 
# Implement the ProductOfNumbers class:
# 
# 
# ProductOfNumbers() Initializes the object with an empty stream.
# void add(int num) Appends the integer num to the stream.
# int getProduct(int k) Returns the product of the last k numbers in the
# current list. You can assume that always the current list has at least k
# numbers.
# 
# 
# The test cases are generated so that, at any time, the product of any
# contiguous sequence of numbers will fit into a single 32-bit integer without
# overflowing.
# 
# 
# Example:
# 
# 
# Input
# 
# ["ProductOfNumbers","add","add","add","add","add","getProduct","getProduct","getProduct","add","getProduct"]
# [[],[3],[0],[2],[5],[4],[2],[3],[4],[8],[2]]
# 
# Output
# [null,null,null,null,null,null,20,40,0,null,32]
# 
# Explanation
# ProductOfNumbers productOfNumbers = new ProductOfNumbers();
# productOfNumbers.add(3);        // [3]
# productOfNumbers.add(0);        // [3,0]
# productOfNumbers.add(2);        // [3,0,2]
# productOfNumbers.add(5);        // [3,0,2,5]
# productOfNumbers.add(4);        // [3,0,2,5,4]
# productOfNumbers.getProduct(2); // return 20. The product of the last 2
# numbers is 5 * 4 = 20
# productOfNumbers.getProduct(3); // return 40. The product of the last 3
# numbers is 2 * 5 * 4 = 40
# productOfNumbers.getProduct(4); // return 0. The product of the last 4
# numbers is 0 * 2 * 5 * 4 = 0
# productOfNumbers.add(8);        // [3,0,2,5,4,8]
# productOfNumbers.getProduct(2); // return 32. The product of the last 2
# numbers is 4 * 8 = 32 
# 
# 
# 
# Constraints:
# 
# 
# 0 <= num <= 100
# 1 <= k <= 4 * 10^4
# At most 4 * 10^4 calls will be made to add and getProduct.
# The product of the stream at any point in time will fit in a 32-bit
# integer.
# 
# 
# 
# Follow-up: Can you implement both GetProduct and Add to work in O(1) time
# complexity instead of O(k) time complexity?
#

# @lc code=start
from __future__ import annotations


class ProductOfNumbers:

    def __init__(self):
        self.prefix_products = [1]

    def add(self, num: int) -> None:
        if num == 0:
            self.prefix_products = [1]
        else:
            self.prefix_products.append(self.prefix_products[-1] * num)

    def getProduct(self, k: int) -> int:
        if k >= len(self.prefix_products):
            return 0
        return self.prefix_products[-1] // self.prefix_products[-k - 1]


# Your ProductOfNumbers object will be instantiated and called as such:
# obj = ProductOfNumbers()
# obj.add(num)
# param_2 = obj.getProduct(k)
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Products over a suffix can be answered like prefix sums: product of last `k`
# numbers is `prefix[-1] / prefix[-k-1]`. The only complication is zero, because
# division across a zero is invalid and any product containing zero is 0.
#
# Data structure:
# `prefix_products` stores cumulative products since the most recent zero. It
# starts with sentinel 1 so division works when asking for all stored numbers.
#
# Walkthrough:
# 1. On nonzero add, append previous prefix product times `num`.
# 2. On zero, reset to `[1]`; any query reaching before this reset includes a
#    zero and must return 0.
# 3. For `getProduct(k)`, if `k` is at least the number of values since the last
#    zero, return 0. Otherwise divide two prefix products.
#
# Edge cases:
# - Multiple zeros: every zero just resets the prefix list.
# - `k` exactly equals the count since last zero: division by sentinel 1 works.
# - Query includes a zero: detected by `k >= len(prefix_products)`.
#
# Complexity:
# - `add`: O(1).
# - `getProduct`: O(1).
# - Space: O(m), where m is the number of consecutive nonzero values since the
#   last zero.
