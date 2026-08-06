#
# @lc app=leetcode id=3303 lang=python3
#
# [3303] Find the Occurrence of First Almost Equal Substring
#
# https://leetcode.com/problems/find-the-occurrence-of-first-almost-equal-substring/description/
#
# algorithms
# Hard (16.11%)
# Likes:    79
# Dislikes: 9
# Total Accepted:    5.9K
# Total Submissions: 36.4K
# Testcase Example:  "\"abcdefg\"\n\"bcdffg\""
#
#
# You are given two strings s and pattern.
#
# A string x is called almost equal to y if you can change at most one
# character in x to make it identical to y.
#
# Return the smallest starting index of a substring in s that is almost
# equal to pattern. If no such index exists, return -1.
#
# A substring is a contiguous non-empty sequence of characters within a
# string.
#
# Example 1:
#
# Input: s = "abcdefg", pattern = "bcdffg"
#
# Output: 1
#
# Explanation:
#
# The substring s[1..6] == "bcdefg" can be converted to "bcdffg" by
# changing s[4] to "f".
#
# Example 2:
#
# Input: s = "ababbababa", pattern = "bacaba"
#
# Output: 4
#
# Explanation:
#
# The substring s[4..9] == "bababa" can be converted to "bacaba" by
# changing s[6] to "c".
#
# Example 3:
#
# Input: s = "abcd", pattern = "dba"
#
# Output: -1
#
# Example 4:
#
# Input: s = "dde", pattern = "d"
#
# Output: 0
#
# Constraints:
#
# 1 <= pattern.length < s.length <= 10^5
#
# s and pattern consist only of lowercase English letters.
#
# Follow-up: Could you solve the problem if at most k consecutive
# characters can be changed?
#

# @lc code=start
class Solution:
    def minStartingIndex(self, s: str, pattern: str) -> int:
        """
        Interview explanation:
        Find the leftmost window of s that differs from pattern in at most one
        character (almost equal substring).

        Algorithm:
        - Z-array of pattern + '#' + s gives longest prefix match at each start.
        - Z-array of reversed pattern/s gives longest suffix match.
        - Start i is valid iff prefix_match + suffix_match >= m - 1.

        Complexity: O(n + m) time, O(n + m) space.
        """
        def z_function(t: str) -> list[int]:
            n = len(t)
            z = [0] * n
            l = r = 0
            for i in range(1, n):
                if i < r:
                    z[i] = min(r - i, z[i - l])
                while i + z[i] < n and t[z[i]] == t[i + z[i]]:
                    z[i] += 1
                if i + z[i] > r:
                    l, r = i, i + z[i]
            return z

        m, n = len(pattern), len(s)
        z1 = z_function(pattern + "#" + s)
        z2 = z_function(pattern[::-1] + "#" + s[::-1])
        for i in range(n - m + 1):
            pref = z1[m + 1 + i]
            suf = z2[m + 1 + (n - (i + m))]
            if pref + suf >= m - 1:
                return i
        return -1
# @lc code=end
