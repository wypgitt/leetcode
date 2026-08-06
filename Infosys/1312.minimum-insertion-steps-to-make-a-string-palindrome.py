#
# @lc app=leetcode id=1312 lang=python3
#
# [1312] Minimum Insertion Steps to Make a String Palindrome
#
# https://leetcode.com/problems/minimum-insertion-steps-to-make-a-string-palindrome/description/
#
# algorithms
# Hard (74.31%)
# Likes:    5676
# Dislikes: 78
# Total Accepted:    341K
# Total Submissions: 459K
# Testcase Example:  "\"zzazz\""
#
# Given a string s. In one step you can insert any character at any index of
# the string.
#
# Return the minimum number of steps to make s palindrome.
#
# A Palindrome String is one that reads the same backward as well as forward.
#
# Example 1:
#
# Input: s = "zzazz"
# Output: 0
# Explanation: The string "zzazz" is already palindrome we do not need any
# insertions.
#
# Example 2:
#
# Input: s = "mbadm"
# Output: 2
# Explanation: String can be "mbdadbm" or "mdbabdm".
#
# Example 3:
#
# Input: s = "leetcode"
# Output: 5
# Explanation: Inserting 5 characters the string becomes "leetcodocteel".
#
# Constraints:
#
# 1 <= s.length <= 500
#
# s consists of lowercase English letters.
#

# @lc code=start
class Solution:
    def minInsertions(self, s: str) -> int:
        """
        Interview explanation:
        Min insertions to make palindrome = n - LPS(s). LPS length equals LCS
        of s and reverse(s). Classic palindrome DP.

        Algorithm (LCS with reverse):
        - Compute LCS(s, s[::-1]) via DP; return n - LCS.

        Complexity: O(n^2) time, O(n^2) space (can roll to O(n)).
        """
        n = len(s)
        t = s[::-1]
        dp = [[0] * (n + 1) for _ in range(n + 1)]
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if s[i - 1] == t[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
        return n - dp[n][n]

    def minInsertions_interval_dp(self, s: str) -> int:
        """
        Interview explanation:
        Alternate interval DP: dp[i][j] = min insertions for s[i..j].
        If s[i]==s[j]: dp[i+1][j-1]; else 1+min(dp[i+1][j], dp[i][j-1]).

        Algorithm:
        - Length-increasing interval DP as above.

        Complexity: O(n^2) time, O(n^2) space.
        """
        n = len(s)
        dp = [[0] * n for _ in range(n)]
        for length in range(2, n + 1):
            for i in range(n - length + 1):
                j = i + length - 1
                if s[i] == s[j]:
                    dp[i][j] = dp[i + 1][j - 1]
                else:
                    dp[i][j] = 1 + min(dp[i + 1][j], dp[i][j - 1])
        return dp[0][n - 1]
# @lc code=end

