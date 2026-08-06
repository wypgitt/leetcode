#
# @lc app=leetcode id=1009 lang=python3
#
# [1009] Complement of Base 10 Integer
#
# https://leetcode.com/problems/complement-of-base-10-integer/description/
#
# algorithms
# Easy (63.4%)
# Likes:    2857
# Dislikes: 146
# Total Accepted:    456K
# Total Submissions: 719K
# Testcase Example:  "5"
#
# The complement of an integer is the integer you get when you flip all the 0's
# to 1's and all the 1's to 0's in its binary representation.
#
# For example, The integer 5 is "101" in binary and its complement is "010"
# which is the integer 2.
#
# Given an integer n, return its complement.
#
# Example 1:
#
# Input: n = 5
# Output: 2
# Explanation: 5 is "101" in binary, with complement "010" in binary, which is
# 2 in base-10.
#
# Example 2:
#
# Input: n = 7
# Output: 0
# Explanation: 7 is "111" in binary, with complement "000" in binary, which is
# 0 in base-10.
#
# Example 3:
#
# Input: n = 10
# Output: 5
# Explanation: 10 is "1010" in binary, with complement "0101" in binary, which
# is 5 in base-10.
#
# Constraints:
#
# 0 <= n < 10^9
#
# Note: This question is the same as 476:
# https://leetcode.com/problems/number-complement/
#

# @lc code=start
class Solution:
    def bitwiseComplement(self, n: int) -> int:
        """
        Interview explanation:
        Complement flips all bits in the binary representation (no leading zeros).
        Build a mask of same bit-width (all 1s) and XOR with n. Special case n=0 → 1.

        Algorithm:
        - If n==0: return 1
        - mask = 1; while mask<=n: mask<<=1; return (mask-1)^n

        Complexity: O(log n) time, O(1) space.
        """
        if n == 0:
            return 1
        mask = 1
        while mask <= n:
            mask <<= 1
        return (mask - 1) ^ n

    def bitwiseComplement_str(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: convert to binary string, flip '0'↔'1', parse back.

        Algorithm:
        - ''.join('1' if c=='0' else '0' for c in bin(n)[2:]); int(..., 2)

        Complexity: O(log n) time and space.
        """
        return int("".join("1" if c == "0" else "0" for c in bin(n)[2:]), 2)
# @lc code=end
