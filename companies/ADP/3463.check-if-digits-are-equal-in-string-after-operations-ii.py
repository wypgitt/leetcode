#
# @lc app=leetcode id=3463 lang=python3
#
# [3463] Check If Digits Are Equal in String After Operations II
#
# https://leetcode.com/problems/check-if-digits-are-equal-in-string-after-operations-ii/description/
#
# algorithms
# Hard (14.53%)
# Likes:    112
# Dislikes: 56
# Total Accepted:    14.1K
# Total Submissions: 97.1K
# Testcase Example:  "\"3902\""
#
#
# You are given a string s consisting of digits. Perform the following
# operation repeatedly until the string has exactly two digits:
#
# For each pair of consecutive digits in s, starting from the first digit,
# calculate a new digit as the sum of the two digits modulo 10.
#
# Replace s with the sequence of newly calculated digits, maintaining the
# order in which they are computed.
#
# Return true if the final two digits in s are the same; otherwise, return
# false.
#
# Example 1:
#
# Input: s = "3902"
#
# Output: true
#
# Explanation:
#
# Initially, s = "3902"
#
# First operation:
#
# (s[0] + s[1]) % 10 = (3 + 9) % 10 = 2
#
# (s[1] + s[2]) % 10 = (9 + 0) % 10 = 9
#
# (s[2] + s[3]) % 10 = (0 + 2) % 10 = 2
#
# s becomes "292"
#
# Second operation:
#
# (s[0] + s[1]) % 10 = (2 + 9) % 10 = 1
#
# (s[1] + s[2]) % 10 = (9 + 2) % 10 = 1
#
# s becomes "11"
#
# Since the digits in "11" are the same, the output is true.
#
# Example 2:
#
# Input: s = "34789"
#
# Output: false
#
# Explanation:
#
# Initially, s = "34789".
#
# After the first operation, s = "7157".
#
# After the second operation, s = "862".
#
# After the third operation, s = "48".
#
# Since '4' != '8', the output is false.
#
# Constraints:
#
# 3 <= s.length <= 10^5
#
# s consists of only digits.
#

# @lc code=start
import math


class Solution:
    def hasSameDigits(self, s: str) -> bool:
        """
        Interview explanation:
        After n-2 rounds, each final digit is a binomial-weighted sum of the
        original digits mod 10. Compare the two weighted sums.

        Algorithm:
        - Final digit i equals sum_j C(n-2, j) * s[i+j] mod 10 (i in {0,1}).
        - Compute C(n-2, j) mod 10 via Lucas mod 2 and 5, CRT lookup table.
        - Accumulate both finals; return equality.

        Complexity: O(n log n) time (Lucas per index), O(1) space.
        """
        n = len(s)
        num1 = num2 = 0
        for i in range(n - 1):
            coefficient = self._nCkMod10(n - 2, i)
            num1 = (num1 + coefficient * int(s[i])) % 10
            num2 = (num2 + coefficient * int(s[i + 1])) % 10
        return num1 == num2

    def _nCkMod10(self, n: int, k: int) -> int:
        """C(n, k) mod 10 via Lucas mod 2/5 and CRT table."""
        mod2 = self._lucas(n, k, 2)
        mod5 = self._lucas(n, k, 5)
        # CRT combinations of residues mod 2 and mod 5.
        lookup = [
            [0, 6, 2, 8, 4],  # mod2 == 0
            [5, 1, 7, 3, 9],  # mod2 == 1
        ]
        return lookup[mod2][mod5]

    def _lucas(self, n: int, k: int, prime: int) -> int:
        res = 1
        while n > 0 or k > 0:
            n_mod, k_mod = n % prime, k % prime
            res = res * math.comb(n_mod, k_mod) % prime
            n //= prime
            k //= prime
        return res
# @lc code=end

