#
# @lc app=leetcode id=3352 lang=python3
#
# [3352] Count K-Reducible Numbers Less Than N
#
# https://leetcode.com/problems/count-k-reducible-numbers-less-than-n/description/
#
# algorithms
# Hard (28.70%)
# Likes:    65
# Dislikes: 3
# Total Accepted:    4.9K
# Total Submissions: 17K
# Testcase Example:  "\"111\"\n1"
#
#
# You are given a binary string s representing a number n in its binary
# form.
#
# You are also given an integer k.
#
# An integer x is called k-reducible if performing the following operation
# at most k times reduces it to 1:
#
# Replace x with the count of set bits in its binary representation.
#
# For example, the binary representation of 6 is "110". Applying the
# operation once reduces it to 2 (since "110" has two set bits). Applying
# the operation again to 2 (binary "10") reduces it to 1 (since "10" has
# one set bit).
#
# Return an integer denoting the number of positive integers less than n
# that are k-reducible.
#
# Since the answer may be too large, return it modulo 10^9 + 7.
#
# Example 1:
#
# Input: s = "111", k = 1
#
# Output: 3
#
# Explanation:
#
# n = 7. The 1-reducible integers less than 7 are 1, 2, and 4.
#
# Example 2:
#
# Input: s = "1000", k = 2
#
# Output: 6
#
# Explanation:
#
# n = 8. The 2-reducible integers less than 8 are 1, 2, 3, 4, 5, and 6.
#
# Example 3:
#
# Input: s = "1", k = 3
#
# Output: 0
#
# Explanation:
#
# There are no positive integers less than n = 1, so the answer is 0.
#
# Constraints:
#
# 1 <= s.length <= 800
#
# s has no leading zeros.
#
# s consists only of the characters '0' and '1'.
#
# 1 <= k <= 5
#

# @lc code=start

from functools import cache


class Solution:
    def countKReducibleNumbers(self, s: str, k: int) -> int:
        """
        Interview explanation:
        x is k-reducible if ≤k popcount-reductions reach 1. For x>1 this is
        1 + ops(popcount(x)) ≤ k. Count positive integers < n (binary s).

        Algorithm:
        - Precompute ops[i] = steps for i→1 via popcount (i ≤ len(s)).
        - Binary digit DP (< n): at end with not tight, count cnt>0 and
          ops[cnt] < k (≡ 1+ops[cnt] ≤ k; includes 1 when k≥1).

        Complexity: O(len(s)^2) time/space for DP states.
        """
        MOD = 10**9 + 7
        n = len(s)
        ops = [0] * (n + 1)
        for i in range(2, n + 1):
            ops[i] = ops[i.bit_count()] + 1

        @cache
        def dp(i: int, cnt: int, tight: bool) -> int:
            if i == n:
                # tight means we formed exactly n — need strictly less than n
                if tight:
                    return 0
                return int(cnt > 0 and ops[cnt] < k)
            up = int(s[i]) if tight else 1
            res = 0
            for d in range(up + 1):
                res += dp(i + 1, cnt + d, tight and d == up)
            return res % MOD

        return dp(0, 0, True)
# @lc code=end
