#
# @lc app=leetcode id=1318 lang=python3
#
# [1318] Minimum Flips to Make a OR b Equal to c
#
# https://leetcode.com/problems/minimum-flips-to-make-a-or-b-equal-to-c/description/
#
# algorithms
# Medium (71.97%)
# Likes:    2146
# Dislikes: 112
# Total Accepted:    199.2K
# Total Submissions: 276.8K
# Testcase Example:  '2\n6\n5'
#
# Given 3 positives numbers a, b and c. Return the minimum flips required in
# some bits of a and b to make ( a OR b == c ). (bitwise OR operation).
# Flip operation consists of change any single bit 1 to 0 or change the bit 0
# to 1 in their binary representation.
# 
# 
# Example 1:
# 
# 
# 
# 
# Input: a = 2, b = 6, c = 5
# Output: 3
# Explanation: After flips a = 1 , b = 4 , c = 5 such that (a OR b == c)
# 
# Example 2:
# 
# 
# Input: a = 4, b = 2, c = 7
# Output: 1
# 
# 
# Example 3:
# 
# 
# Input: a = 1, b = 2, c = 3
# Output: 0
# 
# 
# 
# Constraints:
# 
# 
# 1 <= a <= 10^9
# 1 <= b <= 10^9
# 1 <= c <= 10^9
# 
#

# @lc code=start
from __future__ import annotations


class Solution:
    def minFlips(self, a: int, b: int, c: int) -> int:
        flips = 0

        while a or b or c:
            bit_a = a & 1
            bit_b = b & 1
            bit_c = c & 1

            if bit_c == 1:
                if bit_a == 0 and bit_b == 0:
                    flips += 1
            else:
                flips += bit_a + bit_b

            a >>= 1
            b >>= 1
            c >>= 1

        return flips
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Bitwise OR is independent per bit, so we can solve one bit position at a
# time. For each position, compare `(a_bit | b_bit)` with `c_bit` and count the
# minimum flips needed.
#
# Cases:
# - If `c_bit` is 1, at least one of `a_bit` or `b_bit` must be 1. If both are
#   0, flip one of them.
# - If `c_bit` is 0, both `a_bit` and `b_bit` must be 0. Flip every 1 among
#   them.
#
# Why this is optimal:
# Bits do not interact. A flip in one bit position cannot help another bit
# position, so the sum of local minimums is the global minimum.
#
# Edge cases:
# - Already valid: returns 0.
# - `c` has a 1 where both `a` and `b` are 0: one flip.
# - `c` has a 0 where both `a` and `b` are 1: two flips.
#
# Complexity:
# - Time: O(log max(a,b,c)), one iteration per significant bit.
# - Space: O(1).
