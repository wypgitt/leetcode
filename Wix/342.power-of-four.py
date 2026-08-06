#
# @lc app=leetcode id=342 lang=python3
#
# [342] Power of Four
#
# https://leetcode.com/problems/power-of-four/description/
#
# algorithms
# Easy (52.41%)
# Likes:    4514
# Dislikes: 424
# Total Accepted:    1.1M
# Total Submissions: 2.2M
# Testcase Example:  "16"
#
# Given an integer n, return true if it is a power of four. Otherwise, return
# false.
#
# An integer n is a power of four, if there exists an integer x such that n ==
# 4^x.
#
# Example 1:
#
# Input: n = 16
# Output: true
#
# Example 2:
#
# Input: n = 5
# Output: false
#
# Example 3:
#
# Input: n = 1
# Output: true
#
# Constraints:
#
# -2^31 <= n <= 2^31 - 1
#
# Follow up: Could you solve it without loops/recursion?
#

# @lc code=start
class Solution:
    def isPowerOfFour(self, n: int) -> bool:
        """
        Interview explanation:
        Power of four is a power of two with the single set bit in an even
        position. Check n > 0, n&(n-1)==0 (power of two), and n & 0x55555555
        (bit only on even indices).

        Algorithm:
        - Return n > 0 and (n & (n - 1)) == 0 and (n & 0x55555555) != 0.

        Complexity: O(1) time and space.
        """
        return n > 0 and (n & (n - 1)) == 0 and (n & 0x55555555) != 0
# @lc code=end
