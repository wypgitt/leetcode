#
# @lc app=leetcode id=326 lang=python3
#
# [326] Power of Three
#
# https://leetcode.com/problems/power-of-three/description/
#
# algorithms
# Easy (51.42%)
# Likes:    3745
# Dislikes: 319
# Total Accepted:    1.4M
# Total Submissions: 2.8M
# Testcase Example:  "27"
#
# Given an integer n, return true if it is a power of three. Otherwise, return
# false.
#
# An integer n is a power of three, if there exists an integer x such that n ==
# 3^x.
#
# Example 1:
#
# Input: n = 27
# Output: true
# Explanation: 27 = 3^3
#
# Example 2:
#
# Input: n = 0
# Output: false
# Explanation: There is no x where 3^x = 0.
#
# Example 3:
#
# Input: n = -1
# Output: false
# Explanation: There is no x where 3^x = (-1).
#
# Constraints:
#
# -2^31 <= n <= 2^31 - 1
#
# Follow up: Could you solve it without loops/recursion?
#

# @lc code=start
class Solution:
    def isPowerOfThree(self, n: int) -> bool:
        """
        Interview explanation:
        Math: max power of 3 fitting in 32-bit signed int is 3^19 = 1162261467.
        n is a power of 3 iff n > 0 and that max power is divisible by n.

        Algorithm:
        - Return n > 0 and 1162261467 % n == 0.

        Complexity: O(1) time and space.
        """
        return n > 0 and 1162261467 % n == 0

    def isPowerOfThree_loop(self, n: int) -> bool:
        """
        Interview explanation:
        Alternate: repeatedly divide by 3 while divisible; succeed iff end at 1.

        Algorithm:
        - While n % 3 == 0 and n > 0: n //= 3; return n == 1.

        Complexity: O(log n) time, O(1) space.
        """
        if n <= 0:
            return False
        while n % 3 == 0:
            n //= 3
        return n == 1
# @lc code=end
