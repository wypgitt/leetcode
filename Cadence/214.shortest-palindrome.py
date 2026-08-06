#
# @lc app=leetcode id=214 lang=python3
#
# [214] Shortest Palindrome
#
# https://leetcode.com/problems/shortest-palindrome/description/
#
# algorithms
# Hard (42.88%)
# Likes:    4618
# Dislikes: 295
# Total Accepted:    371K
# Total Submissions: 866K
# Testcase Example:  "\"aacecaaa\""
#
# You are given a string s. You can convert s to a palindrome by adding
# characters in front of it.
#
# Return the shortest palindrome you can find by performing this
# transformation.
#
# Example 1:
#
# Input: s = "aacecaaa"
# Output: "aaacecaaa"
#
# Example 2:
#
# Input: s = "abcd"
# Output: "dcbabcd"
#
# Constraints:
#
# 0 <= s.length <= 5 * 10^4
#
# s consists of lowercase English letters only.
#

# @lc code=start
class Solution:
    def shortestPalindrome(self, s: str) -> str:
        """
        Interview explanation:
        We need the shortest prefix to prepend so the whole string is a palindrome.
        That means finding the longest palindromic prefix of s, then prepending
        the reverse of the remaining suffix. KMP on s + '#' + reverse(s) finds
        that longest prefix via the final LPS value.

        Algorithm:
        - Let rev = s[::-1]; build pattern = s + '#' + rev.
        - Compute KMP longest-prefix-suffix (LPS) array.
        - longest = lps[-1]; prepend reverse of s[longest:].

        Complexity: O(n) time, O(n) space.
        """
        if not s:
            return s
        rev = s[::-1]
        comb = s + "#" + rev
        n = len(comb)
        lps = [0] * n
        length = 0
        i = 1
        while i < n:
            if comb[i] == comb[length]:
                length += 1
                lps[i] = length
                i += 1
            elif length:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
        longest = lps[-1]
        return rev[: len(s) - longest] + s
# @lc code=end
