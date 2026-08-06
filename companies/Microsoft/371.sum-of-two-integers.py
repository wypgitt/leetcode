#
# @lc app=leetcode id=371 lang=python3
#
# [371] Sum of Two Integers
#
# https://leetcode.com/problems/sum-of-two-integers/description/
#
# algorithms
# Medium (55.91%)
# Likes:    4759
# Dislikes: 5902
# Total Accepted:    736K
# Total Submissions: 1.3M
# Testcase Example:  "1"
#
# Given two integers a and b, return the sum of the two integers without using
# the operators + and -.
#
# Example 1:
#
# Input: a = 1, b = 2
# Output: 3
#
# Example 2:
#
# Input: a = 2, b = 3
# Output: 5
#
# Constraints:
#
# -1000 <= a, b <= 1000
#

# @lc code=start
class Solution:
    def getSum(self, a: int, b: int) -> int:
        """
        Interview explanation:
        Add without +/− using bitwise XOR (sum without carry) and AND<<1 (carry).
        Python ints are unbounded, so mask to 32-bit two's complement like Java/C.

        Algorithm:
        - MASK = 0xFFFFFFFF; loop while carry (b) is nonzero.
        - a, b = (a ^ b) & MASK, ((a & b) << 1) & MASK
        - If a > MAX_INT (sign bit set), convert to negative via ~(a ^ MASK).

        Complexity: O(1) iterations (≤32), O(1) space.
        """
        MASK = 0xFFFFFFFF
        MAX_INT = 0x7FFFFFFF
        while b != 0:
            a, b = (a ^ b) & MASK, ((a & b) << 1) & MASK
        return a if a <= MAX_INT else ~(a ^ MASK)
# @lc code=end
