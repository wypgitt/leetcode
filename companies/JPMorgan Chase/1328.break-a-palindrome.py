#
# @lc app=leetcode id=1328 lang=python3
#
# [1328] Break a Palindrome
#
# https://leetcode.com/problems/break-a-palindrome/description/
#
# algorithms
# Medium (51.63%)
# Likes:    2460
# Dislikes: 755
# Total Accepted:    202K
# Total Submissions: 391K
# Testcase Example:  "\"abccba\""
#
# Given a palindromic string of lowercase English letters palindrome, replace
# exactly one character with any lowercase English letter so that the resulting
# string is not a palindrome and that it is the lexicographically smallest one
# possible.
#
# Return the resulting string. If there is no way to replace a character to
# make it not a palindrome, return an empty string.
#
# A string a is lexicographically smaller than a string b (of the same length)
# if in the first position where a and b differ, a has a character strictly
# smaller than the corresponding character in b. For example, "abcc" is
# lexicographically smaller than "abcd" because the first position they differ
# is at the fourth character, and 'c' is smaller than 'd'.
#
# Example 1:
#
# Input: palindrome = "abccba"
# Output: "aaccba"
# Explanation: There are many ways to make "abccba" not a palindrome, such as
# "zbccba", "aaccba", and "abacba".
# Of all the ways, "aaccba" is the lexicographically smallest.
#
# Example 2:
#
# Input: palindrome = "a"
# Output: ""
# Explanation: There is no way to replace a single character to make "a" not a
# palindrome, so return an empty string.
#
# Constraints:
#
# 1 <= palindrome.length <= 1000
#
# palindrome consists of only lowercase English letters.
#

# @lc code=start
class Solution:
    def breakPalindrome(self, palindrome: str) -> str:
        """
        Interview explanation:
        Replace exactly one char to get lexicographically smallest non-palindrome.
        If length 1 impossible ("" ). Prefer change first non-'a' in first half
        to 'a'; else change last char to 'b'.

        Algorithm:
        - n==1 -> ""; else scan [0..n//2); else s[:-1]+'b'.

        Complexity: O(n) time, O(n) space.
        """
        n = len(palindrome)
        if n == 1:
            return ""
        chars = list(palindrome)
        for i in range(n // 2):
            if chars[i] != "a":
                chars[i] = "a"
                return "".join(chars)
        chars[-1] = "b"
        return "".join(chars)
# @lc code=end

