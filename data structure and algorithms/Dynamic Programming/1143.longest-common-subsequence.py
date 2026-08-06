#
# @lc app=leetcode id=1143 lang=python3
#
# [1143] Longest Common Subsequence
#
# https://leetcode.com/problems/longest-common-subsequence/description/
#
# algorithms
# Medium (59.44%)
# Likes:    15249
# Dislikes: 252
# Total Accepted:    1.9M
# Total Submissions: 3.3M
# Testcase Example:  "\"abcde\""
#
# Given two strings text1 and text2, return the length of their longest common
# subsequence. If there is no common subsequence, return 0.
#
# A subsequence of a string is a new string generated from the original string
# with some characters (can be none) deleted without changing the relative
# order of the remaining characters.
#
# For example, "ace" is a subsequence of "abcde".
#
# A common subsequence of two strings is a subsequence that is common to both
# strings.
#
# Example 1:
#
# Input: text1 = "abcde", text2 = "ace"
# Output: 3
# Explanation: The longest common subsequence is "ace" and its length is 3.
#
# Example 2:
#
# Input: text1 = "abc", text2 = "abc"
# Output: 3
# Explanation: The longest common subsequence is "abc" and its length is 3.
#
# Example 3:
#
# Input: text1 = "abc", text2 = "def"
# Output: 0
# Explanation: There is no such common subsequence, so the result is 0.
#
# Constraints:
#
# 1 <= text1.length, text2.length <= 1000
#
# text1 and text2 consist of only lowercase English characters.
#

# @lc code=start
class Solution:
    def longestCommonSubsequence(self, text1: str, text2: str) -> int:
        """
        Interview explanation:
        Classic LCS length via 2D DP: dp[i][j] = LCS of prefixes text1[:i], text2[:j].

        Algorithm (DP):
        - If equal chars: dp[i][j] = dp[i-1][j-1]+1 else max(dp[i-1][j], dp[i][j-1]).

        Complexity: O(mn) time, O(mn) space.
        """
        m, n = len(text1), len(text2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i - 1] == text2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        return dp[m][n]

    def longestCommonSubsequence_space(self, text1: str, text2: str) -> int:
        """
        Interview explanation:
        Space-optimized LCS: only previous row needed → two 1D arrays (or one
        with careful updates).

        Algorithm:
        - Keep prev/cur rows of length n+1; roll after each i.

        Complexity: O(mn) time, O(min(m,n)) space (here O(n)).
        """
        if len(text1) < len(text2):
            text1, text2 = text2, text1
        m, n = len(text1), len(text2)
        prev = [0] * (n + 1)
        for i in range(1, m + 1):
            cur = [0] * (n + 1)
            for j in range(1, n + 1):
                if text1[i - 1] == text2[j - 1]:
                    cur[j] = prev[j - 1] + 1
                else:
                    cur[j] = max(prev[j], cur[j - 1])
            prev = cur
        return prev[n]
# @lc code=end
