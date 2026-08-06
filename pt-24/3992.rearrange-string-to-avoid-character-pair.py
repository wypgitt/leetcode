#
# @lc app=leetcode id=3992 lang=python3
#
# [3992] Rearrange String to Avoid Character Pair
#
# https://leetcode.com/problems/rearrange-string-to-avoid-character-pair/description/
#
# algorithms
# Easy (78.13%)
# Likes:    29
# Dislikes: 1
# Total Accepted:    40.2K
# Total Submissions: 51.5K
# Testcase Example:  "\"aabc\"\n\"a\"\n\"c\""
#
#
# You are given a string s and two distinct lowercase English letters x
# and y.
#
# Rearrange the characters of s to construct a new string t such that:
#
# t is a permutation of s.
#
# Every occurrence of y appears before every occurrence of x in t.
#
# Return any valid string t.
#
# Example 1:
#
# Input: s = "aabc", x = "a", y = "c"
#
# Output: "cbaa"
#
# Explanation:
#
# The string "cbaa" is a permutation of "aabc", and every occurrence of
# 'c' appears before every occurrence of 'a'.
#
# Example 2:
#
# Input: s = "dcab", x = "d", y = "b"
#
# Output: "cabd"
#
# Explanation:
#
# The string "cabd" is a permutation of "dcab", and every occurrence of
# 'b' appears before every occurrence of 'd'.
#
# Example 3:
#
# Input: s = "axe", x = "o", y = "x"
#
# Output: "axe"
#
# Explanation:
#
# The string "axe" is already valid. Since 'o' does not occur in the
# string, the required condition is automatically satisfied.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists of lowercase English letters.
#
# x and y are lowercase English letters.
#
# x != y
#

# @lc code=start
class Solution:
    def rearrangeString(self, s: str, x: str, y: str) -> str:
        """
        Interview explanation:
        Any permutation is fine as long as every y appears before every x.
        Move all y characters to the front (stable for the rest).

        Algorithm:
        - Partition: write all y first via in-place swaps, keep relative order
          of non-y characters after them.

        Complexity: O(n) time, O(n) space for the character list.
        """
        t = list(s)
        i = 0
        for j, c in enumerate(t):
            if c == y:
                t[i], t[j] = c, t[i]
                i += 1
        return "".join(t)

    def rearrangeString_count(self, s: str, x: str, y: str) -> str:
        """
        Interview explanation:
        Alternate: rebuild as (all y) + (chars that are neither) + (all x).

        Algorithm:
        - Count / filter characters into three groups and concatenate.

        Complexity: O(n) time and space.
        """
        ys = [c for c in s if c == y]
        mid = [c for c in s if c != x and c != y]
        xs = [c for c in s if c == x]
        return "".join(ys + mid + xs)
# @lc code=end
