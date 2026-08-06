#
# @lc app=leetcode id=3519 lang=python3
#
# [3519] Count Numbers with Non-Decreasing Digits 
#
# https://leetcode.com/problems/count-numbers-with-non-decreasing-digits/description/
#
# algorithms
# Hard (39.05%)
# Likes:    65
# Dislikes: 4
# Total Accepted:    7.4K
# Total Submissions: 18.9K
# Testcase Example:  "\"23\"\n\"28\"\n8"
#
#
# You are given two integers, l and r, represented as strings, and an
# integer b. Return the count of integers in the inclusive range [l, r]
# whose digits are in non-decreasing order when represented in base b.
#
# An integer is considered to have non-decreasing digits if, when read
# from left to right (from the most significant digit to the least
# significant digit), each digit is greater than or equal to the previous
# one.
#
# Since the answer may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: l = "23", r = "28", b = 8
#
# Output: 3
#
# Explanation:
#
# The numbers from 23 to 28 in base 8 are: 27, 30, 31, 32, 33, and 34.
#
# Out of these, 27, 33, and 34 have non-decreasing digits. Hence, the
# output is 3.
#
# Example 2:
#
# Input: l = "2", r = "7", b = 2
#
# Output: 2
#
# Explanation:
#
# The numbers from 2 to 7 in base 2 are: 10, 11, 100, 101, 110, and 111.
#
# Out of these, 11 and 111 have non-decreasing digits. Hence, the output
# is 2.
#
# Constraints:
#
# 1 <= l.length <= r.length <= 100
#
# 2 <= b <= 10
#
# l and r consist only of digits.
#
# The value represented by l is less than or equal to the value
# represented by r.
#
# l and r do not contain leading zeros.
#

# @lc code=start
from typing import List
import functools


class Solution:
    def countNumbers(self, l: str, r: str, b: int) -> int:
        """
        Interview explanation:
        Count integers in [l, r] whose base-b digits are non-decreasing.
        Convert bounds to base b and use digit DP; answer = F(r) - F(l-1).

        Algorithm:
        - Convert decimal string to base-b digit list (big-integer style).
        - Digit DP(pos, last_digit, tight): place non-decreasing digits.
        - Leading zeros via last_digit=0 padding to equal length.

        Complexity: O(len^2 * b + len * b^2) with conversion/DP; mod 1e9+7.
        """
        MOD = 10**9 + 7

        def decrement(s: str) -> str:
            chars = list(s)
            i = len(chars) - 1
            while i >= 0 and chars[i] == "0":
                chars[i] = "9"
                i -= 1
            if i < 0:
                return "0"
            chars[i] = str(int(chars[i]) - 1)
            res = "".join(chars).lstrip("0")
            return res if res else "0"

        def to_base(num: str, base: int) -> List[int]:
            cur = [0]
            for ch in num:
                d = ord(ch) - 48
                carry = 0
                for i in range(len(cur)):
                    prod = cur[i] * 10 + carry
                    cur[i] = prod % base
                    carry = prod // base
                while carry:
                    cur.append(carry % base)
                    carry //= base
                carry = d
                i = 0
                while carry:
                    if i == len(cur):
                        cur.append(0)
                    sm = cur[i] + carry
                    cur[i] = sm % base
                    carry = sm // base
                    i += 1
            while len(cur) > 1 and cur[-1] == 0:
                cur.pop()
            return cur[::-1]

        def count_upto(digits: List[int]) -> int:
            n = len(digits)

            @functools.lru_cache(None)
            def dp(pos: int, last: int, tight: bool) -> int:
                if pos == n:
                    return 1
                lim = digits[pos] if tight else b - 1
                res = 0
                for d in range(last, lim + 1):
                    res = (res + dp(pos + 1, d, tight and d == lim)) % MOD
                return res

            return dp(0, 0, True)

        r_dig = to_base(r, b)
        l_dig = to_base(decrement(l), b)
        # pad l_dig to r length with leading zeros for consistent DP
        if len(l_dig) < len(r_dig):
            l_dig = [0] * (len(r_dig) - len(l_dig)) + l_dig
        return (count_upto(r_dig) - count_upto(l_dig) + MOD) % MOD
# @lc code=end
