#
# @lc app=leetcode id=1281 lang=python3
#
# [1281] Subtract the Product and Sum of Digits of an Integer
#
# https://leetcode.com/problems/subtract-the-product-and-sum-of-digits-of-an-integer/description/
#
# algorithms
# Easy (86.58%)
# Likes:    2865
# Dislikes: 255
# Total Accepted:    699K
# Total Submissions: 807K
# Testcase Example:  "234"
#
# Given an integer number n, return the difference between the product of its
# digits and the sum of its digits.
#
# Example 1:
#
# Input: n = 234
# Output: 15
# Explanation:
# Product of digits = 2 * 3 * 4 = 24
# Sum of digits = 2 + 3 + 4 = 9
# Result = 24 - 9 = 15
#
# Example 2:
#
# Input: n = 4421
# Output: 21
# Explanation:
# Product of digits = 4 * 4 * 2 * 1 = 32
# Sum of digits = 4 + 4 + 2 + 1 = 11
# Result = 32 - 11 = 21
#
# Constraints:
#
# 1 <= n <= 10^5
#

# @lc code=start

class Solution:
    def subtractProductAndSum(self, n: int) -> int:
        """
        Interview explanation:
        Compute product of digits minus sum of digits of n.

        Algorithm:
        - prod=1; s=0; while n: d=n%10; prod*=d; s+=d; n//=10; return prod-s.

        Complexity: O(log n) time, O(1) space.
        """
        prod, s = 1, 0
        while n:
            d = n % 10
            prod *= d
            s += d
            n //= 10
        return prod - s

    def subtractProductAndSum_str(self, n: int) -> int:
        """
        Interview explanation:
        Alternate via digit characters.

        Algorithm:
        - digits=[int(c) for c in str(n)]; product-sum.

        Complexity: O(log n) time/space.
        """
        digits = [int(c) for c in str(n)]
        prod = 1
        for d in digits:
            prod *= d
        return prod - sum(digits)
# @lc code=end
