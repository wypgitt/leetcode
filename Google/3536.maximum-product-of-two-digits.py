#
# @lc app=leetcode id=3536 lang=python3
#
# [3536] Maximum Product of Two Digits
#
# https://leetcode.com/problems/maximum-product-of-two-digits/description/
#
# algorithms
# Easy (75.76%)
# Likes:    308
# Dislikes: 6
# Total Accepted:    203.8K
# Total Submissions: 269K
# Testcase Example:  "31"
#
#
# You are given a positive integer n.
#
# Return the maximum product of any two digits in n.
#
# Note: You may use the same digit twice if it appears more than once in
# n.
#
# Example 1:
#
# Input: n = 31
#
# Output: 3
#
# Explanation:
#
# The digits of n are [3, 1].
#
# The possible products of any two digits are: 3 * 1 = 3.
#
# The maximum product is 3.
#
# Example 2:
#
# Input: n = 22
#
# Output: 4
#
# Explanation:
#
# The digits of n are [2, 2].
#
# The possible products of any two digits are: 2 * 2 = 4.
#
# The maximum product is 4.
#
# Example 3:
#
# Input: n = 124
#
# Output: 8
#
# Explanation:
#
# The digits of n are [1, 2, 4].
#
# The possible products of any two digits are: 1 * 2 = 2, 1 * 4 = 4, 2 * 4
# = 8.
#
# The maximum product is 8.
#
# Constraints:
#
# 10 <= n <= 10^9
#

# @lc code=start
class Solution:
    def maxProduct(self, n: int) -> int:
        """
        Interview explanation:
        Product of two digits is maximized by the two largest digits in n
        (with replacement only if a digit repeats).

        Algorithm:
        - Scan digits; track largest and second-largest.
        - Return their product.

        Complexity: O(log n) time, O(1) space.
        """
        a = b = 0
        x = n
        while x:
            d = x % 10
            if d >= a:
                b = a
                a = d
            elif d > b:
                b = d
            x //= 10
        return a * b

    def maxProduct_sort(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: sort digit characters descending and multiply the top two.

        Algorithm:
        - digits = sorted(str(n), reverse=True); return int(digits[0])*int(digits[1]).

        Complexity: O(log n * log log n) time, O(log n) space.
        """
        digits = sorted(str(n), reverse=True)
        return int(digits[0]) * int(digits[1])
# @lc code=end
