#
# @lc app=leetcode id=730 lang=python3
#
# [730] Count Different Palindromic Subsequences
#
# https://leetcode.com/problems/count-different-palindromic-subsequences/description/
#
# algorithms
# Hard (48.05%)
# Likes:    2014
# Dislikes: 104
# Total Accepted:    47.0K
# Total Submissions: 97.8K
# Testcase Example:  "\"bccb\""
#
# Given a string s, return the number of different non-empty palindromic
# subsequences in s. Since the answer may be very large, return it modulo 10^9
# + 7.
#
# A subsequence of a string is obtained by deleting zero or more characters
# from the string.
#
# A sequence is palindromic if it is equal to the sequence reversed.
#
# Two sequences a_1, a_2, ... and b_1, b_2, ... are different if there is some
# i for which a_i != b_i.
#
# Example 1:
#
# Input: s = "bccb"
# Output: 6
# Explanation: The 6 different non-empty palindromic subsequences are 'b', 'c',
# 'bb', 'cc', 'bcb', 'bccb'.
# Note that 'bcb' is counted only once, even though it occurs twice.
#
# Example 2:
#
# Input: s = "abcdabcdabcdabcdabcdabcdabcdabcddcbadcbadcbadcbadcbadcbadcbadcba"
# Output: 104860361
# Explanation: There are 3104860382 different non-empty palindromic
# subsequences, which is 104860361 modulo 10^9 + 7.
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s[i] is either 'a', 'b', 'c', or 'd'.
#


# @lc code=start
class Solution:
    def countPalindromicSubsequences(self, s: str) -> int:
        """
        Interview explanation:
        Count distinct palindromic subsequences via interval DP. dp[i][j] =
        number of distinct palindromic subsequences in s[i..j]. For each pair
        (i,j), consider characters that appear as both ends; handle duplicates
        carefully by finding innermost/outermost occurrences.

        Algorithm:
        - Let dp[i][i] = 1
        - For length L from 2..n, for i, j = i+L-1:
          - If s[i] != s[j]: dp[i][j] = dp[i+1][j] + dp[i][j-1] - dp[i+1][j-1]
          - Else: find leftmost/rightmost k,l with s[k]=s[l]=s[i] in (i,j):
            - none: 2*dp[i+1][j-1] + 2
            - one: 2*dp[i+1][j-1] + 1
            - two+: 2*dp[i+1][j-1] - dp[k+1][l-1]
        - Mod 10^9+7; answer dp[0][n-1]

        Complexity: O(n^2) time and space.
        """
        MOD = 10**9 + 7
        n = len(s)
        dp = [[0] * n for _ in range(n)]
        for i in range(n):
            dp[i][i] = 1
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                if s[i] != s[j]:
                    dp[i][j] = dp[i + 1][j] + dp[i][j - 1] - dp[i + 1][j - 1]
                else:
                    left, right = i + 1, j - 1
                    while left <= right and s[left] != s[i]:
                        left += 1
                    while left <= right and s[right] != s[i]:
                        right -= 1
                    if left > right:
                        dp[i][j] = dp[i + 1][j - 1] * 2 + 2
                    elif left == right:
                        dp[i][j] = dp[i + 1][j - 1] * 2 + 1
                    else:
                        dp[i][j] = dp[i + 1][j - 1] * 2 - dp[left + 1][right - 1]
                dp[i][j] %= MOD
        return dp[0][n - 1] % MOD
# @lc code=end

