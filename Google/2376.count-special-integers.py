#
# @lc app=leetcode id=2376 lang=python3
#
# [2376] Count Special Integers
#
# https://leetcode.com/problems/count-special-integers/description/
#
# algorithms
# Hard (44.49%)
# Likes:    652
# Dislikes: 35
# Total Accepted:    19.6K
# Total Submissions: 44.1K
# Testcase Example:  "20"
#
# We call a positive integer special if all of its digits are distinct.
#
# Given a positive integer n, return the number of special integers that belong
# to the interval [1, n].
#
#
#
# Example 1:
#
# Input: n = 20
# Output: 19
# Explanation: All the integers from 1 to 20, except 11, are special. Thus,
# there are 19 special integers.
#
# Example 2:
#
# Input: n = 5
# Output: 5
# Explanation: All the integers from 1 to 5 are special.
#
# Example 3:
#
# Input: n = 135
# Output: 110
# Explanation: There are 110 integers from 1 to 135 that are special.
# Some of the integers that are not special are: 22, 114, and 131.
#
#
#
# Constraints:
#
#
# 1 <= n <= 2 * 10^9
#

# @lc code=start

from functools import lru_cache


class Solution:
    def countSpecialNumbers(self, n: int) -> int:
        """
        Interview explanation:
        Count positive integers <= n whose digits are all distinct.

        Algorithm:
        - Digit DP: pos, used-mask, tight, started; skip reused digits once
          started; count completed numbers.

        Complexity: O(d * 2^10) time/space (d = number of digits).
        """
        digits = list(map(int, str(n)))

        @lru_cache(None)
        def dp(i: int, mask: int, tight: bool, started: bool) -> int:
            if i == len(digits):
                return int(started)
            up = digits[i] if tight else 9
            res = 0
            for d in range(up + 1):
                if started and (mask >> d) & 1:
                    continue
                nstarted = started or d > 0
                nmask = mask | (1 << d) if nstarted else mask
                res += dp(i + 1, nmask, tight and d == up, nstarted)
            return res

        return dp(0, 0, True, False)

    def countSpecialNumbers_math(self, n: int) -> int:
        """
        Interview explanation:
        Alternate: combinatorics for shorter lengths + digit-by-digit for same
        length as n (no leading-zero paths mixed with shorter counts).

        Algorithm:
        - Sum P(9,L-1)*9 for len < m; then for same length pick digits left-to-right.

        Complexity: O(d^2) time, O(1) space.
        """
        s = list(map(int, str(n)))
        m = len(s)

        def perm(a: int, b: int) -> int:
            res = 1
            for i in range(b):
                res *= a - i
            return res

        ans = 0
        for L in range(1, m):
            ans += 9 * perm(9, L - 1)

        used = [False] * 10
        for i, dig in enumerate(s):
            for d in range(0 if i else 1, dig):
                if used[d]:
                    continue
                ans += perm(10 - (i + 1), m - i - 1)
            if used[dig]:
                break
            used[dig] = True
        else:
            ans += 1  # n itself is special
        return ans
# @lc code=end
