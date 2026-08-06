#
# @lc app=leetcode id=516 lang=python3
#
# [516] Longest Palindromic Subsequence
#
# https://leetcode.com/problems/longest-palindromic-subsequence/description/
#
# algorithms
# Medium (65.76%)
# Likes:    10488
# Dislikes: 347
# Total Accepted:    813K
# Total Submissions: 1.2M
# Testcase Example:  "\"bbbab\""
#
# Given a string s, find the longest palindromic subsequence's length in s.
#
# A subsequence is a sequence that can be derived from another sequence by
# deleting some or no elements without changing the order of the remaining
# elements.
#
# Example 1:
#
# Input: s = "bbbab"
# Output: 4
# Explanation: One possible longest palindromic subsequence is "bbbb".
#
# Example 2:
#
# Input: s = "cbbd"
# Output: 2
# Explanation: One possible longest palindromic subsequence is "bb".
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s consists only of lowercase English letters.
#

# @lc code=start
class Solution:
    def longestPalindromeSubseq(self, s: str) -> int:
        """
        Interview explanation:
        Interval DP: dp[i][j] = LPS length in s[i..j]. If ends match, add 2 to
        the inner LPS; else take the better of dropping either end. Equivalent
        to LCS(s, reverse(s)).

        Algorithm:
        - Base: dp[i][i] = 1.
        - For length L from 2..n, fill intervals of that length.
        - Return dp[0][n-1].

        Complexity: O(n^2) time and space.
        """
        n = len(s)
        dp = [[0] * n for _ in range(n)]
        for i in range(n):
            dp[i][i] = 1
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                if s[i] == s[j]:
                    dp[i][j] = 2 + (dp[i + 1][j - 1] if i + 1 <= j - 1 else 0)
                else:
                    dp[i][j] = max(dp[i + 1][j], dp[i][j - 1])
        return dp[0][n - 1]
# @lc code=end
