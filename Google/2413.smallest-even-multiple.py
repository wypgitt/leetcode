#
# @lc app=leetcode id=2413 lang=python3
#
# [2413] Smallest Even Multiple
#
# https://leetcode.com/problems/smallest-even-multiple/description/
#
# algorithms
# Easy (88.49%)
# Likes:    1093
# Dislikes: 128
# Total Accepted:    317.6K
# Total Submissions: 359K
# Testcase Example:  "5"
#
# Given a positive integer n, return the smallest positive integer that is a
# multiple of both 2 and n.
#
#
#
# Example 1:
#
# Input: n = 5
# Output: 10
# Explanation: The smallest multiple of both 5 and 2 is 10.
#
# Example 2:
#
# Input: n = 6
# Output: 6
# Explanation: The smallest multiple of both 6 and 2 is 6. Note that a number is
# a multiple of itself.
#
#
#
# Constraints:
#
#
# 1 <= n <= 150
#

# @lc code=start
class Solution:
    def smallestEvenMultiple(self, n: int) -> int:
        """
        Interview explanation:
        Smallest positive integer divisible by both 2 and n (LCM(2,n)).

        Algorithm:
        - If n even return n else 2n.

        Complexity: O(1) time/space.
        """
        return n if n % 2 == 0 else n * 2

    def smallestEvenMultiple_math(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: LCM(2, n) = 2*n // gcd(2,n).

        Algorithm:
        - Use math.gcd.

        Complexity: O(1) time/space.
        """
        import math
        return 2 * n // math.gcd(2, n)
# @lc code=end
