#
# @lc app=leetcode id=2429 lang=python3
#
# [2429] Minimize XOR
#
# https://leetcode.com/problems/minimize-xor/description/
#
# algorithms
# Medium (62.25%)
# Likes:    1102
# Dislikes: 78
# Total Accepted:    140.9K
# Total Submissions: 226.4K
# Testcase Example:  "3\n5"
#
# Given two positive integers num1 and num2, find the positive integer x such
# that:
#
#
# x has the same number of set bits as num2, and
#
#
# The value x XOR num1 is minimal.
#
# Note that XOR is the bitwise XOR operation.
#
# Return the integer x. The test cases are generated such that x is uniquely
# determined.
#
# The number of set bits of an integer is the number of 1's in its binary
# representation.
#
#
#
# Example 1:
#
# Input: num1 = 3, num2 = 5
# Output: 3
# Explanation:
# The binary representations of num1 and num2 are 0011 and 0101, respectively.
# The integer 3 has the same number of set bits as num2, and the value 3 XOR 3 =
# 0 is minimal.
#
# Example 2:
#
# Input: num1 = 1, num2 = 12
# Output: 3
# Explanation:
# The binary representations of num1 and num2 are 0001 and 1100, respectively.
# The integer 3 has the same number of set bits as num2, and the value 3 XOR 1 =
# 2 is minimal.
#
#
#
# Constraints:
#
#
# 1 <= num1, num2 <= 10^9
#

# @lc code=start
class Solution:
    def minimizeXor(self, num1: int, num2: int) -> int:
        """
        Interview explanation:
        Find x with same popcount as num2 minimizing x XOR num1 (prefer bits of
        num1 set, then fill low bits).

        Algorithm:
        - Need k = popcount(num2) bits in x. Set bits from high of num1 first;
          if still need bits, set lowest unset bits.

        Complexity: O(32) time, O(1) space.
        """
        k = num2.bit_count()
        x = 0
        for b in range(31, -1, -1):
            if k and (num1 & (1 << b)):
                x |= 1 << b
                k -= 1
        for b in range(32):
            if k and not (x & (1 << b)):
                x |= 1 << b
                k -= 1
        return x

    def minimizeXor_bit(self, num1: int, num2: int) -> int:
        """
        Interview explanation:
        Alternate bit construction with the same priority rules.

        Algorithm:
        - Same as primary.

        Complexity: O(1) time/space.
        """
        return self.minimizeXor(num1, num2)
# @lc code=end
