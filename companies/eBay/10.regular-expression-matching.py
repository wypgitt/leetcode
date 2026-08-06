#
# @lc app=leetcode id=10 lang=python3
#
# [10] Regular Expression Matching
#
# https://leetcode.com/problems/regular-expression-matching/description/
#
# algorithms
# Hard (31.5%)
# Likes:    13443
# Dislikes: 2413
# Total Accepted:    1.5M
# Total Submissions: 4.6M
# Testcase Example:  "\"aa\""
#
# Given an input string s and a pattern p, implement regular expression
# matching with support for '.' and '*' where:
#
# '.' Matches any single character.
#
# '*' Matches zero or more of the preceding element.
#
# Return a boolean indicating whether the matching covers the entire input
# string (not partial).
#
# Example 1:
#
# Input: s = "aa", p = "a"
# Output: false
# Explanation: "a" does not match the entire string "aa".
#
# Example 2:
#
# Input: s = "aa", p = "a*"
# Output: true
# Explanation: '*' means zero or more of the preceding element, 'a'. Therefore,
# by repeating 'a' once, it becomes "aa".
#
# Example 3:
#
# Input: s = "ab", p = ".*"
# Output: true
# Explanation: ".*" means "zero or more (*) of any character (.)".
#
# Constraints:
#
# 1 <= s.length <= 20
#
# 1 <= p.length <= 20
#
# s contains only lowercase English letters.
#
# p contains only lowercase English letters, '.', and '*'.
#
# It is guaranteed for each appearance of the character '*', there will be a
# previous valid character to match.
#

# @lc code=start
class Solution:
    def isMatch(self, s: str, p: str) -> bool:
        """
        Interview explanation:
        Classic regex DP on prefixes. dp[i][j] means s[:i] matches p[:j].
        '.' matches any single char; 'x*' matches zero or more of x (or '.').

        Algorithm:
        - dp[0][0] = True; empty matches empty.
        - Initialize first row for patterns like a*, a*b*, etc. matching "".
        - For each (i, j):
          - If p[j-1] is '.' or equals s[i-1], take dp[i-1][j-1].
          - If p[j-1] is '*', either use zero of the preceding atom
            (dp[i][j-2]) or one more match when the atom fits s[i-1]
            (dp[i-1][j]).

        Complexity: O(mn) time and space.
        """
        m, n = len(s), len(p)
        dp = [[False] * (n + 1) for _ in range(m + 1)]
        dp[0][0] = True

        for j in range(2, n + 1):
            if p[j - 1] == "*":
                dp[0][j] = dp[0][j - 2]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if p[j - 1] == "." or p[j - 1] == s[i - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                elif p[j - 1] == "*":
                    dp[i][j] = dp[i][j - 2]
                    if p[j - 2] == "." or p[j - 2] == s[i - 1]:
                        dp[i][j] = dp[i][j] or dp[i - 1][j]

        return dp[m][n]
# @lc code=end
