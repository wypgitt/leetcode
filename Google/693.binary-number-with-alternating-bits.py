#
# @lc app=leetcode id=693 lang=python3
#
# [693] Binary Number with Alternating Bits
#
# https://leetcode.com/problems/binary-number-with-alternating-bits/description/
#
# algorithms
# Easy (69.98%)
# Likes:    1732
# Dislikes: 125
# Total Accepted:    311K
# Total Submissions: 444K
# Testcase Example:  "5"
#
# Given a positive integer, check whether it has alternating bits: namely, if
# two adjacent bits will always have different values.
#
# Example 1:
#
# Input: n = 5
# Output: true
# Explanation: The binary representation of 5 is: 101
#
# Example 2:
#
# Input: n = 7
# Output: false
# Explanation: The binary representation of 7 is: 111.
#
# Example 3:
#
# Input: n = 11
# Output: false
# Explanation: The binary representation of 11 is: 1011.
#
# Constraints:
#
# 1 <= n <= 2^31 - 1
#

# @lc code=start
class Solution:
    def hasAlternatingBits(self, n: int) -> bool:
        """
        Interview explanation:
        Bits should alternate 0/1. Trick: n ^ (n>>1) yields all 1s in the bit
        width of n; check x & (x+1) == 0 for x = n^(n>>1).

        Algorithm:
        - x = n ^ (n >> 1); return x & (x + 1) == 0.

        Complexity: O(1) time/space.
        """
        x = n ^ (n >> 1)
        return (x & (x + 1)) == 0
# @lc code=end
