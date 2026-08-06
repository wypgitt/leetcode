#
# @lc app=leetcode id=115 lang=python3
#
# [115] Distinct Subsequences
#
# https://leetcode.com/problems/distinct-subsequences/description/
#
# algorithms
# Hard (52.33%)
# Likes:    7504
# Dislikes: 321
# Total Accepted:    742K
# Total Submissions: 1.4M
# Testcase Example:  "\"rabbbit\""
#
# Given two strings s and t, return the number of distinct subsequences of s
# which equals t.
#
# The test cases are generated so that the answer fits on a 32-bit signed
# integer.
#
# Example 1:
#
# Input: s = "rabbbit", t = "rabbit"
# Output: 3
# Explanation:
# As shown below, there are 3 ways you can generate "rabbit" from s.
# rabbbit
# rabbbit
# rabbbit
#
# Example 2:
#
# Input: s = "babgbag", t = "bag"
# Output: 5
# Explanation:
# As shown below, there are 5 ways you can generate "bag" from s.
# babgbag
# babgbag
# babgbag
# babgbag
# babgbag
#
# Constraints:
#
# 1 <= s.length, t.length <= 1000
#
# s and t consist of English letters.
#

# @lc code=start
class Solution:
    def numDistinct(self, s: str, t: str) -> int:
        """
        Interview explanation:
        Count ways to form t as a subsequence of s with 1D DP. Process s left
        to right and update counts for t from the end so we reuse previous
        column values in place.

        Algorithm:
        - dp[j] = number of ways to form t[:j] from the prefix of s seen so far.
        - dp[0] = 1 (empty target).
        - For each char s[i], for j from |t| down to 1: if s[i] == t[j-1],
          add dp[j-1] into dp[j].

        Complexity: O(|s| * |t|) time, O(|t|) space.
        """
        n = len(t)
        dp = [0] * (n + 1)
        dp[0] = 1
        for ch in s:
            for j in range(n, 0, -1):
                if ch == t[j - 1]:
                    dp[j] += dp[j - 1]
        return dp[n]
# @lc code=end
