#
# @lc app=leetcode id=3622 lang=python3
#
# [3622] Check Divisibility by Digit Sum and Product
#
# https://leetcode.com/problems/check-divisibility-by-digit-sum-and-product/description/
#
# algorithms
# Easy (69.63%)
# Likes:    59
# Dislikes: 1
# Total Accepted:    76.7K
# Total Submissions: 110.1K
# Testcase Example:  "99"
#
#
# You are given a positive integer n. Determine whether n is divisible by
# the sum of the following two values:
#
# The digit sum of n (the sum of its digits).
#
# The digit product of n (the product of its digits).
#
# Return true if n is divisible by this sum; otherwise, return false.
#
# Example 1:
#
# Input: n = 99
#
# Output: true
#
# Explanation:
#
# Since 99 is divisible by the sum (9 + 9 = 18) plus product (9 * 9 = 81)
# of its digits (total 99), the output is true.
#
# Example 2:
#
# Input: n = 23
#
# Output: false
#
# Explanation:
#
# Since 23 is not divisible by the sum (2 + 3 = 5) plus product (2 * 3 =
# 6) of its digits (total 11), the output is false.
#
# Constraints:
#
# 1 <= n <= 10^6
#

# @lc code=start

class Solution:
    def checkDivisibility(self, n: int) -> bool:
        """
        Interview explanation:
        Check whether n is divisible by (digit_sum(n) + digit_product(n)).

        Algorithm:
        - Scan digits once, accumulating sum and product.
        - Return n % (sum + product) == 0.

        Complexity: O(log n) time, O(1) space.
        """
        x = n
        digit_sum = 0
        digit_product = 1
        while x:
            d = x % 10
            digit_sum += d
            digit_product *= d
            x //= 10
        return n % (digit_sum + digit_product) == 0

    def checkDivisibility_str(self, n: int) -> bool:
        """
        Interview explanation:
        Alternate: convert to string and fold digits.

        Algorithm:
        - digits = map(int, str(n)); compute sum and product; check modulo.

        Complexity: O(log n) time, O(log n) space.
        """
        digits = [int(ch) for ch in str(n)]
        total = sum(digits)
        prod = 1
        for d in digits:
            prod *= d
        return n % (total + prod) == 0
# @lc code=end

