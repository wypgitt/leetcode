#
# @lc app=leetcode id=1638 lang=python3
#
# [1638] Count Substrings That Differ by One Character
#
# https://leetcode.com/problems/count-substrings-that-differ-by-one-character/description/
#
# algorithms
# Medium (72.31%)
# Likes:    1208
# Dislikes: 357
# Total Accepted:    38.8K
# Total Submissions: 53.7K
# Testcase Example:  "\"aba\""
#
# Given two strings s and t, find the number of ways you can choose a non-empty
# substring of s and replace a single character by a different character such
# that the resulting substring is a substring of t. In other words, find the
# number of substrings in s that differ from some substring in t by exactly one
# character.
#
# For example, the underlined substrings in "computer" and "computation" only
# differ by the 'e'/'a', so this is a valid way.
#
# Return the number of substrings that satisfy the condition above.
#
# A substring is a contiguous sequence of characters within a string.
#
# Example 1:
#
# Input: s = "aba", t = "baba"
# Output: 6
# Explanation: The following are the pairs of substrings from s and t that
# differ by exactly 1 character:
# ("aba", "baba")
# ("aba", "baba")
# ("aba", "baba")
# ("aba", "baba")
# ("aba", "baba")
# ("aba", "baba")
# The underlined portions are the substrings that are chosen from s and t.
#
# Example 2:
#
# Input: s = "ab", t = "bb"
# Output: 3
# Explanation: The following are the pairs of substrings from s and t that
# differ by 1 character:
# ("ab", "bb")
# ("ab", "bb")
# ("ab", "bb")
# The underlined portions are the substrings that are chosen from s and t.
#
# Constraints:
#
# 1 <= s.length, t.length <= 100
#
# s and t consist of lowercase English letters only.
#

# @lc code=start
class Solution:
    def countSubstrings(self, s: str, t: str) -> int:
        """
        Interview explanation:
        Count pairs of equal-length substrings of s,t that differ in exactly one
        character. DP: for each alignment, track runs of equal/diff.

        Algorithm (DP expand):
        - For each start alignment (i,j), walk forward counting positions with
          exactly one mismatch so far — classic O(|s|*|t|) DP:
          dp[i][j] = consecutive equals ending at i,j; also track one-diff counts.

        Complexity: O(|s|*|t|) time/space (can roll).
        """
        m, n = len(s), len(t)
        ans = 0
        # dpl[i][j]: longest equal suffix of s[:i], t[:j]
        # For each pair of starting points expand
        for i in range(m):
            for j in range(n):
                diff = 0
                k = 0
                while i + k < m and j + k < n:
                    if s[i + k] != t[j + k]:
                        diff += 1
                    if diff > 1:
                        break
                    if diff == 1:
                        ans += 1
                    k += 1
        return ans

    def countSubstrings_dp(self, s: str, t: str) -> int:
        """
        Interview explanation:
        Alternate DP formulation: same_same and one_diff ending at (i,j).

        Algorithm (DP):
        - same[i][j], diff[i][j] transitions; sum all diff[i][j].

        Complexity: O(mn) time/space.
        """
        m, n = len(s), len(t)
        # same[i][j]: # of equal-ending substrings (all equal) ending at i-1,j-1
        same = [[0] * (n + 1) for _ in range(m + 1)]
        diff = [[0] * (n + 1) for _ in range(m + 1)]
        ans = 0
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s[i - 1] == t[j - 1]:
                    same[i][j] = same[i - 1][j - 1] + 1
                    diff[i][j] = diff[i - 1][j - 1]
                else:
                    same[i][j] = 0
                    diff[i][j] = same[i - 1][j - 1] + 1
                ans += diff[i][j]
        return ans
# @lc code=end
