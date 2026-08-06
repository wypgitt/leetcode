#
# @lc app=leetcode id=2595 lang=python3
#
# [2595] Number of Even and Odd Bits
#
# https://leetcode.com/problems/number-of-even-and-odd-bits/description/
#
# algorithms
# Easy (73.92%)
# Likes:    381
# Dislikes: 119
# Total Accepted:    75.1K
# Total Submissions: 101.6K
# Testcase Example:  "50"
#
# You are given a positive integer n.
#
# Let even denote the number of even indices in the binary representation of n
# with value 1.
#
# Let odd denote the number of odd indices in the binary representation of n
# with value 1.
#
# Note that bits are indexed from right to left in the binary representation of
# a number.
#
# Return the array [even, odd].
#
#
#
# Example 1:
#
# Input: n = 50
#
# Output: [1,2]
#
# Explanation:
#
# The binary representation of 50 is 110010.
#
# It contains 1 on indices 1, 4, and 5.
#
# Example 2:
#
# Input: n = 2
#
# Output: [0,1]
#
# Explanation:
#
# The binary representation of 2 is 10.
#
# It contains 1 only on index 1.
#
#
#
# Constraints:
#
#
# 1 <= n <= 1000
#

# @lc code=start
from typing import List


class Solution:
    def evenOddBit(self, n: int) -> List[int]:
        """
        Interview explanation:
        Count set bits at even and odd indices in the binary representation (0-based from LSB).

        Algorithm:
        - Walk bits of n; tally by index parity.

        Complexity: O(log n) time, O(1) space.
        """
        even = odd = 0
        i = 0
        while n:
            if n & 1:
                if i % 2 == 0:
                    even += 1
                else:
                    odd += 1
            n >>= 1
            i += 1
        return [even, odd]

    def evenOddBit_bit(self, n: int) -> List[int]:
        """
        Interview explanation:
        Mask even/odd bit positions and popcount.

        Algorithm:
        - even_mask = 0x555... ; odd_mask = 0xAAA...; bit_count.

        Complexity: O(1) time and space for fixed-width ints.
        """
        return [(n & 0x55555555).bit_count(), (n & 0xAAAAAAAA).bit_count()]
# @lc code=end
