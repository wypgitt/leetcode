#
# @lc app=leetcode id=3472 lang=python3
#
# [3472] Longest Palindromic Subsequence After at Most K Operations
#
# https://leetcode.com/problems/longest-palindromic-subsequence-after-at-most-k-operations/description/
#
# algorithms
# Medium (37.57%)
# Likes:    126
# Dislikes: 18
# Total Accepted:    16K
# Total Submissions: 42.5K
# Testcase Example:  "\"abced\"\n2"
#
#
# You are given a string s and an integer k.
#
# In one operation, you can replace the character at any position with the
# next or previous letter in the alphabet (wrapping around so that 'a' is
# after 'z'). For example, replacing 'a' with the next letter results in
# 'b', and replacing 'a' with the previous letter results in 'z'.
# Similarly, replacing 'z' with the next letter results in 'a', and
# replacing 'z' with the previous letter results in 'y'.
#
# Return the length of the longest palindromic subsequence of s that can
# be obtained after performing at most k operations.
#
# Example 1:
#
# Input: s = "abced", k = 2
#
# Output: 3
#
# Explanation:
#
# Replace s[1] with the next letter, and s becomes "acced".
#
# Replace s[4] with the previous letter, and s becomes "accec".
#
# The subsequence "ccc" forms a palindrome of length 3, which is the
# maximum.
#
# Example 2:
#
# Input: s = "aaazzz", k = 4
#
# Output: 6
#
# Explanation:
#
# Replace s[0] with the previous letter, and s becomes "zaazzz".
#
# Replace s[4] with the next letter, and s becomes "zaazaz".
#
# Replace s[3] with the next letter, and s becomes "zaaaaz".
#
# The entire string forms a palindrome of length 6.
#
# Constraints:
#
# 1 <= s.length <= 200
#
# 1 <= k <= 200
#
# s consists of only lowercase English letters.
#

# @lc code=start
import functools


class Solution:
    def longestPalindromicSubsequence(self, s: str, k: int) -> int:
        """
        Interview explanation:
        LPS DP with an extra dimension for remaining operations. Pairing two
        ends costs the circular alphabet distance; or skip one end.

        Algorithm:
        - dp(i, j, op): best LPS in s[i..j] with <= op ops.
        - Equal ends: 2 + dp(i+1, j-1, op).
        - Else: max(skip i, skip j, pair with cost if affordable).

        Complexity: O(n^2 k) time/space.
        """
        @functools.lru_cache(None)
        def dp(i: int, j: int, op: int) -> int:
            if i > j:
                return 0
            if i == j:
                return 1
            if s[i] == s[j]:
                return 2 + dp(i + 1, j - 1, op)
            res = max(dp(i + 1, j, op), dp(i, j - 1, op))
            cost = self._cost(s[i], s[j])
            if cost <= op:
                res = max(res, 2 + dp(i + 1, j - 1, op - cost))
            return res

        return dp(0, len(s) - 1, k)

    def _cost(self, a: str, b: str) -> int:
        dist = abs(ord(a) - ord(b))
        return min(dist, 26 - dist)

    def longestPalindromicSubsequence_bottomup(self, s: str, k: int) -> int:
        """
        Interview explanation:
        Alternate: bottom-up 3D DP by substring length.

        Algorithm:
        - dp[i][j][op] filled by increasing j-i with the same transitions.

        Complexity: O(n^2 k) time/space.
        """
        n = len(s)
        dp = [[[0] * (k + 1) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for op in range(k + 1):
                dp[i][i][op] = 1
        for length in range(1, n):
            for i in range(n - length):
                j = i + length
                for op in range(k + 1):
                    if s[i] == s[j]:
                        dp[i][j][op] = 2 + dp[i + 1][j - 1][op]
                    else:
                        dp[i][j][op] = max(dp[i + 1][j][op], dp[i][j - 1][op])
                        cost = self._cost(s[i], s[j])
                        if cost <= op:
                            dp[i][j][op] = max(
                                dp[i][j][op], 2 + dp[i + 1][j - 1][op - cost]
                            )
        return dp[0][n - 1][k]
# @lc code=end

