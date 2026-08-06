#
# @lc app=leetcode id=1012 lang=python3
#
# [1012] Numbers With Repeated Digits
#
# https://leetcode.com/problems/numbers-with-repeated-digits/description/
#
# algorithms
# Hard (48.18%)
# Likes:    886
# Dislikes: 91
# Total Accepted:    28.5K
# Total Submissions: 59.1K
# Testcase Example:  "20"
#
# Given an integer n, return the number of positive integers in the range [1,
# n] that have at least one repeated digit.
#
# Example 1:
#
# Input: n = 20
# Output: 1
# Explanation: The only positive number (<= 20) with at least 1 repeated digit
# is 11.
#
# Example 2:
#
# Input: n = 100
# Output: 10
# Explanation: The positive numbers (<= 100) with atleast 1 repeated digit are
# 11, 22, 33, 44, 55, 66, 77, 88, 99, and 100.
#
# Example 3:
#
# Input: n = 1000
# Output: 262
#
# Constraints:
#
# 1 <= n <= 10^9
#

# @lc code=start
class Solution:
    def numDupDigitsAtMostN(self, n: int) -> int:
        """
        Interview explanation:
        Count numbers in [1,n] with at least one repeated digit = n - count of
        numbers with all unique digits. Digit DP / combinatorial: count unique-
        digit numbers with fewer digits, then digit-by-digit for same length.

        Algorithm:
        - digits = decimal digits of n
        - Count A: unique-digit nums with len < len(digits)
        - Count B: unique-digit nums with same length, prefix-constrained
        - Return n - (A+B)

        Complexity: O(d^2) time with d<=10, O(d) space.
        """
        s = list(map(int, str(n)))
        d = len(s)

        def P(m: int, k: int) -> int:
            """Permutations P(m,k) = m!/(m-k)!."""
            res = 1
            for i in range(k):
                res *= m - i
            return res

        # unique with fewer digits
        unique = 0
        for i in range(1, d):
            unique += 9 * P(9, i - 1)

        used = set()
        for i, dig in enumerate(s):
            start = 0 if i else 1
            for x in range(start, dig):
                if x in used:
                    continue
                unique += P(9 - i, d - i - 1)
            if dig in used:
                break
            used.add(dig)
        else:
            unique += 1  # n itself has unique digits
        return n - unique

    def numDupDigitsAtMostN_digit_dp(self, n: int) -> int:
        """
        Interview explanation:
        Alternate classic digit DP: dp(pos, mask, tight, started) counts numbers
        <= n with all distinct digits; answer = n - that count (excluding 0).

        Algorithm:
        - Digits of n; recurse over position with used-bitmask, tight flag,
          and whether we've placed a non-leading digit
        - At end: return 1 if started else 0 (don't count 0 as valid positive)

        Complexity: O(d * 2^10 * 2 * 2) states, O(same) space.
        """
        digits = list(map(int, str(n)))
        m = len(digits)
        memo = {}

        def dp(pos: int, mask: int, tight: bool, started: bool) -> int:
            key = (pos, mask, tight, started)
            if key in memo:
                return memo[key]
            if pos == m:
                return 1 if started else 0
            up = digits[pos] if tight else 9
            res = 0
            for dig in range(0, up + 1):
                nt = tight and dig == up
                if not started and dig == 0:
                    res += dp(pos + 1, mask, nt, False)
                else:
                    if mask & (1 << dig):
                        continue
                    res += dp(pos + 1, mask | (1 << dig), nt, True)
            memo[key] = res
            return res

        return n - dp(0, 0, True, False)
# @lc code=end
