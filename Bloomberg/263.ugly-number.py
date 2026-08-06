#
# @lc app=leetcode id=263 lang=python3
#
# [263] Ugly Number
#
# https://leetcode.com/problems/ugly-number/description/
#
# algorithms
# Easy (43.98%)
# Likes:    3923
# Dislikes: 1802
# Total Accepted:    832K
# Total Submissions: 1.9M
# Testcase Example:  "6"
#
# An ugly number is a positive integer which does not have a prime factor other
# than 2, 3, and 5.
#
# Given an integer n, return true if n is an ugly number.
#
# Example 1:
#
# Input: n = 6
# Output: true
# Explanation: 6 = 2 × 3
#
# Example 2:
#
# Input: n = 1
# Output: true
# Explanation: 1 has no prime factors.
#
# Example 3:
#
# Input: n = 14
# Output: false
# Explanation: 14 is not ugly since it includes the prime factor 7.
#
# Constraints:
#
# -2^31 <= n <= 2^31 - 1
#

# @lc code=start
class Solution:
    def isUgly(self, n: int) -> bool:
        """
        Interview explanation:
        Ugly numbers are positive integers whose prime factors are only 2, 3, 5.
        Divide out 2, 3, and 5; what remains must be 1.

        Algorithm:
        - If n <= 0: False.
        - While divisible by 2, 3, or 5, divide.
        - Return n == 1.

        Complexity: O(log n) time, O(1) space.
        """
        if n <= 0:
            return False
        for p in (2, 3, 5):
            while n % p == 0:
                n //= p
        return n == 1
# @lc code=end
