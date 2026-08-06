#
# @lc app=leetcode id=712 lang=python3
#
# [712] Minimum ASCII Delete Sum for Two Strings
#
# https://leetcode.com/problems/minimum-ascii-delete-sum-for-two-strings/description/
#
# algorithms
# Medium (71.1%)
# Likes:    4567
# Dislikes: 129
# Total Accepted:    282K
# Total Submissions: 397K
# Testcase Example:  "\"sea\""
#
# Given two strings s1 and s2, return the lowest ASCII sum of deleted
# characters to make two strings equal.
#
# Example 1:
#
# Input: s1 = "sea", s2 = "eat"
# Output: 231
# Explanation: Deleting "s" from "sea" adds the ASCII value of "s" (115) to the
# sum.
# Deleting "t" from "eat" adds 116 to the sum.
# At the end, both strings are equal, and 115 + 116 = 231 is the minimum sum
# possible to achieve this.
#
# Example 2:
#
# Input: s1 = "delete", s2 = "leet"
# Output: 403
# Explanation: Deleting "dee" from "delete" to turn the string into "let",
# adds 100[d] + 101[e] + 101[e] to the sum.
# Deleting "e" from "leet" adds 101[e] to the sum.
# At the end, both strings are equal to "let", and the answer is
# 100+101+101+101 = 403.
# If instead we turned both strings into "lee" or "eet", we would get answers
# of 433 or 417, which are higher.
#
# Constraints:
#
# 1 <= s1.length, s2.length <= 1000
#
# s1 and s2 consist of lowercase English letters.
#

# @lc code=start
class Solution:
    def minimumDeleteSum(self, s1: str, s2: str) -> int:
        """
        Interview explanation:
        Min ASCII sum of deleted characters to make s1 and s2 equal — equivalent
        to LCS-style DP minimizing delete cost (or maximizing kept ASCII sum).

        Algorithm:
        - dp[i][j] = min delete sum for s1[:i], s2[:j].
        - If s1[i-1]==s2[j-1]: dp[i][j]=dp[i-1][j-1]; else
          min(dp[i-1][j]+ord(s1[i-1]), dp[i][j-1]+ord(s2[j-1])).

        Complexity: O(mn) time/space (can roll to O(min(m,n))).
        """
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for i in range(1, m + 1):
            dp[i][0] = dp[i - 1][0] + ord(s1[i - 1])
        for j in range(1, n + 1):
            dp[0][j] = dp[0][j - 1] + ord(s2[j - 1])
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(
                        dp[i - 1][j] + ord(s1[i - 1]),
                        dp[i][j - 1] + ord(s2[j - 1]),
                    )
        return dp[m][n]
# @lc code=end
