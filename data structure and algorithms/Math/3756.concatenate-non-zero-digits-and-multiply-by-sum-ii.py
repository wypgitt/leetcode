#
# @lc app=leetcode id=3756 lang=python3
#
# [3756] Concatenate Non-Zero Digits and Multiply by Sum II
#
# https://leetcode.com/problems/concatenate-non-zero-digits-and-multiply-by-sum-ii/description/
#
# algorithms
# Medium (42.66%)
# Likes:    433
# Dislikes: 56
# Total Accepted:    94.9K
# Total Submissions: 222.4K
# Testcase Example:  "\"10203004\"\n[[0,7],[1,3],[4,6]]"
#
#
# You are given a string s of length m consisting of digits. You are also
# given a 2D integer array queries, where queries[i] = [l_i, r_i].
#
# For each queries[i], extract the substring s[l_i..r_i]. Then, perform
# the following:
#
# Form a new integer x by concatenating all the non-zero digits from the
# substring in their original order. If there are no non-zero digits, x =
# 0.
#
# Let sum be the sum of digits in x. The answer is x * sum.
#
# Return an array of integers answer where answer[i] is the answer to the
# i^th query.
#
# Since the answers may be very large, return them modulo 10^9 + 7.
#
# Example 1:
#
# Input: s = "10203004", queries = [[0,7],[1,3],[4,6]]
#
# Output: [12340, 4, 9]
#
# Explanation:
#
# s[0..7] = "10203004"
#
# x = 1234
#
# sum = 1 + 2 + 3 + 4 = 10
#
# Therefore, answer is 1234 * 10 = 12340.
#
# s[1..3] = "020"
#
# x = 2
#
# sum = 2
#
# Therefore, the answer is 2 * 2 = 4.
#
# s[4..6] = "300"
#
# x = 3
#
# sum = 3
#
# Therefore, the answer is 3 * 3 = 9.
#
# Example 2:
#
# Input: s = "1000", queries = [[0,3],[1,1]]
#
# Output: [1, 0]
#
# Explanation:
#
# s[0..3] = "1000"
#
# x = 1
#
# sum = 1
#
# Therefore, the answer is 1 * 1 = 1.
#
# s[1..1] = "0"
#
# x = 0
#
# sum = 0
#
# Therefore, the answer is 0 * 0 = 0.
#
# Example 3:
#
# Input: s = "9876543210", queries = [[0,9]]
#
# Output: [444444137]
#
# Explanation:
#
# s[0..9] = "9876543210"
#
# x = 987654321
#
# sum = 9 + 8 + 7 + 6 + 5 + 4 + 3 + 2 + 1 = 45
#
# Therefore, the answer is 987654321 * 45 = 44444444445.
#
# We return 44444444445 modulo (10^9 + 7) = 444444137.
#
# Constraints:
#
# 1 <= m == s.length <= 10^5
#
# s consists of digits only.
#
# 1 <= queries.length <= 10^5
#
# queries[i] = [l_i, r_i]
#
# 0 <= l_i <= r_i < m
#

# @lc code=start
from typing import List


class Solution:
    def sumAndMultiply(self, s: str, queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        For each substring, x is the integer from non-zero digits; answer
        x * digit_sum(x) mod 1e9+7. Many queries need prefix structure.

        Algorithm:
        - Prefix: nonzero-count, value of nonzero-digit number mod MOD, digit sum.
        - Range value = (pref_x[r+1] - pref_x[l] * 10^{cnt[r+1]-cnt[l]}) mod MOD.
        - Multiply by digit-sum difference.

        Complexity: O(n + q) time, O(n) space.
        """
        MOD = 10**9 + 7
        m = len(s)
        pow10 = [1] * (m + 1)
        idx = [0] * (m + 1)
        pref_x = [0] * (m + 1)
        pref_sum = [0] * (m + 1)
        for i, ch in enumerate(s):
            d = ord(ch) - 48
            pow10[i + 1] = (pow10[i] * 10) % MOD
            idx[i + 1] = idx[i] + (1 if d else 0)
            pref_x[i + 1] = (pref_x[i] * 10 + d) % MOD if d else pref_x[i]
            pref_sum[i + 1] = pref_sum[i] + d

        ans = []
        for l, r in queries:
            length = idx[r + 1] - idx[l]
            x = (pref_x[r + 1] - pref_x[l] * pow10[length]) % MOD
            sm = pref_sum[r + 1] - pref_sum[l]
            ans.append((x * sm) % MOD)
        return ans
# @lc code=end
