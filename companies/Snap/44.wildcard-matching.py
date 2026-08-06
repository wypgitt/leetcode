#
# @lc app=leetcode id=44 lang=python3
#
# [44] Wildcard Matching
#
# https://leetcode.com/problems/wildcard-matching/description/
#
# algorithms
# Hard (32.54%)
# Likes:    9225
# Dislikes: 423
# Total Accepted:    925K
# Total Submissions: 2.8M
# Testcase Example:  "\"aa\""
#
# Given an input string (s) and a pattern (p), implement wildcard pattern
# matching with support for '?' and '*' where:
#
# '?' Matches any single character.
#
# '*' Matches any sequence of characters (including the empty sequence).
#
# The matching should cover the entire input string (not partial).
#
# Example 1:
#
# Input: s = "aa", p = "a"
# Output: false
# Explanation: "a" does not match the entire string "aa".
#
# Example 2:
#
# Input: s = "aa", p = "*"
# Output: true
# Explanation: '*' matches any sequence.
#
# Example 3:
#
# Input: s = "cb", p = "?a"
# Output: false
# Explanation: '?' matches 'c', but the second letter is 'a', which does not
# match 'b'.
#
# Constraints:
#
# 0 <= s.length, p.length <= 2000
#
# s contains only lowercase English letters.
#
# p contains only lowercase English letters, '?' or '*'.
#

# @lc code=start
class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        """
        Interview explanation:
        Wildcard DP: '?' matches one char, '*' matches any sequence (including
        empty). dp[i][j] = whether s[:i] matches p[:j].

        Algorithm:
        - dp[0][0] = True; leading '*'s can match empty string.
        - If p[j-1] is '?' or equals s[i-1], dp[i][j] = dp[i-1][j-1].
        - If p[j-1] is '*', dp[i][j] = dp[i][j-1] (empty) or dp[i-1][j]
          (consume one more char).

        Complexity: O(mn) time and space.
        """
        return self.isMatch_dp(s, p)

    def isMatch_dp(self, s: str, p: str) -> bool:
        """
        Interview explanation:
        Explicit 2D DP formulation (same as primary).

        Algorithm:
        - Fill (m+1) x (n+1) boolean table as above.

        Complexity: O(mn) time and space.
        """
        m, n = len(s), len(p)
        dp = [[False] * (n + 1) for _ in range(m + 1)]
        dp[0][0] = True

        for j in range(1, n + 1):
            if p[j - 1] == "*":
                dp[0][j] = dp[0][j - 1]
            else:
                break

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if p[j - 1] == "*":
                    dp[i][j] = dp[i][j - 1] or dp[i - 1][j]
                elif p[j - 1] == "?" or p[j - 1] == s[i - 1]:
                    dp[i][j] = dp[i - 1][j - 1]

        return dp[m][n]

    def isMatch_greedy(self, s: str, p: str) -> bool:
        """
        Interview explanation:
        Greedy two-pointer with backtrack to the last '*'. Often faster in
        practice and uses O(1) space; still correct for wildcard matching.

        Algorithm:
        - Advance i/j on exact/'?' matches.
        - On '*', record star position and match-start; try matching empty
          first, then expand '*' by one char on mismatch via backtrack.
        - Trailing '*'s are accepted at the end.

        Complexity: O(mn) worst-case time, O(1) space.
        """
        i = j = 0
        star = match = -1
        m, n = len(s), len(p)

        while i < m:
            if j < n and (p[j] == "?" or p[j] == s[i]):
                i += 1
                j += 1
            elif j < n and p[j] == "*":
                star = j
                match = i
                j += 1
            elif star != -1:
                j = star + 1
                match += 1
                i = match
            else:
                return False

        while j < n and p[j] == "*":
            j += 1
        return j == n
# @lc code=end
