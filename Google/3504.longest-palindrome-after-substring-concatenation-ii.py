#
# @lc app=leetcode id=3504 lang=python3
#
# [3504] Longest Palindrome After Substring Concatenation II
#
# https://leetcode.com/problems/longest-palindrome-after-substring-concatenation-ii/description/
#
# algorithms
# Hard (18.38%)
# Likes:    95
# Dislikes: 6
# Total Accepted:    6.9K
# Total Submissions: 37.8K
# Testcase Example:  "\"a\"\n\"a\""
#
#
# You are given two strings, s and t.
#
# You can create a new string by selecting a substring from s (possibly
# empty) and a substring from t (possibly empty), then concatenating them
# in order.
#
# Return the length of the longest palindrome that can be formed this way.
#
# Example 1:
#
# Input: s = "a", t = "a"
#
# Output: 2
#
# Explanation:
#
# Concatenating "a" from s and "a" from t results in "aa", which is a
# palindrome of length 2.
#
# Example 2:
#
# Input: s = "abc", t = "def"
#
# Output: 1
#
# Explanation:
#
# Since all characters are different, the longest palindrome is any single
# character, so the answer is 1.
#
# Example 3:
#
# Input: s = "b", t = "aaaa"
#
# Output: 4
#
# Explanation:
#
# Selecting "aaaa" from t is the longest palindrome, so the answer is 4.
#
# Example 4:
#
# Input: s = "abcde", t = "ecdba"
#
# Output: 5
#
# Explanation:
#
# Concatenating "abc" from s and "ba" from t results in "abcba", which is
# a palindrome of length 5.
#
# Constraints:
#
# 1 <= s.length, t.length <= 1000
#
# s and t consist of lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def longestPalindrome(self, s: str, t: str) -> int:
        """
        Interview explanation:
        Same as the I variant with larger n: match a prefix of s to a suffix of t
        (via reverse), then optionally extend with a palindrome in one string.

        Algorithm:
        - Center-expand longest palindrome starting at each index in s / rev(t).
        - DP LCP lengths; maximize 2*LCP + optional starting-palindrome extension.

        Complexity: O(n^2) time and space.
        """
        def expand(u: str, g: List[int], l: int, r: int) -> None:
            while l >= 0 and r < len(u) and u[l] == u[r]:
                g[l] = max(g[l], r - l + 1)
                l -= 1
                r += 1

        def calc(u: str) -> List[int]:
            g = [0] * len(u)
            for i in range(len(u)):
                expand(u, g, i, i)
                expand(u, g, i, i + 1)
            return g

        m, n = len(s), len(t)
        t = t[::-1]
        g1, g2 = calc(s), calc(t)
        ans = max(max(g1), max(g2))
        f = [[0] * (n + 1) for _ in range(m + 1)]
        for i, a in enumerate(s, 1):
            for j, b in enumerate(t, 1):
                if a == b:
                    f[i][j] = f[i - 1][j - 1] + 1
                    ans = max(ans, f[i][j] * 2 + (0 if i >= m else g1[i]))
                    ans = max(ans, f[i][j] * 2 + (0 if j >= n else g2[j]))
        return ans
# @lc code=end
