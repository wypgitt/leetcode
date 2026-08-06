#
# @lc app=leetcode id=2427 lang=python3
#
# [2427] Number of Common Factors
#
# https://leetcode.com/problems/number-of-common-factors/description/
#
# algorithms
# Easy (80.27%)
# Likes:    694
# Dislikes: 14
# Total Accepted:    175.8K
# Total Submissions: 219K
# Testcase Example:  "12\n6"
#
# Given two positive integers a and b, return the number of common factors of a
# and b.
#
# An integer x is a common factor of a and b if x divides both a and b.
#
#
#
# Example 1:
#
# Input: a = 12, b = 6
# Output: 4
# Explanation: The common factors of 12 and 6 are 1, 2, 3, 6.
#
# Example 2:
#
# Input: a = 25, b = 30
# Output: 2
# Explanation: The common factors of 25 and 30 are 1, 5.
#
#
#
# Constraints:
#
#
# 1 <= a, b <= 1000
#

# @lc code=start
import math


class Solution:
    def commonFactors(self, a: int, b: int) -> int:
        """
        Interview explanation:
        Count positive integers dividing both a and b.

        Algorithm:
        - Count divisors of gcd(a,b).

        Complexity: O(sqrt(g)) time, O(1) space.
        """
        g = math.gcd(a, b)
        ans = 0
        i = 1
        while i * i <= g:
            if g % i == 0:
                ans += 1 if i * i == g else 2
            i += 1
        return ans

    def commonFactors_math(self, a: int, b: int) -> int:
        """
        Interview explanation:
        Alternate: same divisor count via loop to sqrt.

        Algorithm:
        - Identical math approach.

        Complexity: O(sqrt(g)) time, O(1) space.
        """
        return self.commonFactors(a, b)
# @lc code=end
