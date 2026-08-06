#
# @lc app=leetcode id=664 lang=python3
#
# [664] Strange Printer
#
# https://leetcode.com/problems/strange-printer/description/
#
# algorithms
# Hard (60.96%)
# Likes:    2804
# Dislikes: 294
# Total Accepted:    165K
# Total Submissions: 271K
# Testcase Example:  "\"aaabbb\""
#
# There is a strange printer with the following two special properties:
#
# The printer can only print a sequence of the same character each time.
#
# At each turn, the printer can print new characters starting from and ending
# at any place and will cover the original existing characters.
#
# Given a string s, return the minimum number of turns the printer needed to
# print it.
#
# Example 1:
#
# Input: s = "aaabbb"
# Output: 2
# Explanation: Print "aaa" first and then print "bbb".
#
# Example 2:
#
# Input: s = "aba"
# Output: 2
# Explanation: Print "aaa" first and then print "b" from the second place of
# the string, which will cover the existing character 'a'.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def strangePrinter(self, s: str) -> int:
        """
        Interview explanation:
        A strange printer paints any contiguous same-character run in one turn.
        Interval DP: min turns to print s[i..j]. When characters match across a
        split, one turn can be shared by extending an earlier paint.

        Algorithm:
        - Collapse consecutive duplicates.
        - dp[i][j] = min turns for s[i:j+1]; dp[i][i] = 1.
        - For length >= 2: dp[i][j] = min over k in [i,j) of
          dp[i][k] + dp[k+1][j] - (1 if s[k] == s[j] else 0).

        Complexity: O(n^3) time, O(n^2) space.
        """
        chars = []
        for c in s:
            if not chars or chars[-1] != c:
                chars.append(c)
        s = "".join(chars)
        n = len(s)
        if n == 0:
            return 0
        dp = [[0] * n for _ in range(n)]
        for i in range(n):
            dp[i][i] = 1
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                dp[i][j] = length
                for k in range(i, j):
                    turns = dp[i][k] + dp[k + 1][j]
                    if s[k] == s[j]:
                        turns -= 1
                    dp[i][j] = min(dp[i][j], turns)
        return dp[0][n - 1]
# @lc code=end
