#
# @lc app=leetcode id=190 lang=python3
#
# [190] Reverse Bits
#
# https://leetcode.com/problems/reverse-bits/description/
#
# algorithms
# Easy (69.04%)
# Likes:    5956
# Dislikes: 1690
# Total Accepted:    1.4M
# Total Submissions: 2.0M
# Testcase Example:  "43261596"
#
# Reverse bits of a given 32 bits signed integer.
#
# Example 1:
#
# Input: n = 43261596
#
# Output: 964176192
#
# Explanation:
#
# Integer
# Binary
#
# 43261596
# 00000010100101000001111010011100
#
# 964176192
# 00111001011110000010100101000000
#
# Example 2:
#
# Input: n = 2147483644
#
# Output: 1073741822
#
# Explanation:
#
# Integer
# Binary
#
# 2147483644
# 01111111111111111111111111111100
#
# 1073741822
# 00111111111111111111111111111110
#
# Constraints:
#
# 0 <= n <= 2^31 - 2
#
# n is even.
#
# Follow up: If this function is called many times, how would you optimize it?
#

# @lc code=start
class Solution:
    def reverseBits(self, n: int) -> int:
        """
        Interview explanation:
        Build the reversed 32-bit value by repeatedly shifting the result left
        and appending the next low bit of n.

        Algorithm:
        - result = 0.
        - For 32 iterations: result = (result << 1) | (n & 1); n >>= 1.
        - Return result.

        Complexity: O(1) time (32 steps), O(1) space.
        """
        result = 0
        for _ in range(32):
            result = (result << 1) | (n & 1)
            n >>= 1
        return result
# @lc code=end
