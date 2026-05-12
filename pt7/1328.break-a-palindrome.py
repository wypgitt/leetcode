#
# @lc app=leetcode id=1328 lang=python3
#
# [1328] Break a Palindrome
#
# https://leetcode.com/problems/break-a-palindrome/description/
#
# algorithms
# Medium (51.59%)
# Likes:    2450
# Dislikes: 755
# Total Accepted:    198.4K
# Total Submissions: 384.5K
# Testcase Example:  '"abccba"'
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
# 
# Example 1:
# 
# 
# Input: palindrome = "abccba"
# Output: "aaccba"
# Explanation: There are many ways to make "abccba" not a palindrome, such as
# "zbccba", "aaccba", and "abacba".
# Of all the ways, "aaccba" is the lexicographically smallest.
# 
# 
# Example 2:
# 
# 
# Input: palindrome = "a"
# Output: ""
# Explanation: There is no way to replace a single character to make "a" not a
# palindrome, so return an empty string.
# 
# 
# 
# Constraints:
# 
# 
# 1 <= palindrome.length <= 1000
# palindrome consists of only lowercase English letters.
# 
# 
#

# @lc code=start
from __future__ import annotations


class Solution:
    def breakPalindrome(self, palindrome: str) -> str:
        if len(palindrome) == 1:
            return ""

        chars = list(palindrome)

        for i in range(len(chars) // 2):
            if chars[i] != "a":
                chars[i] = "a"
                return "".join(chars)

        chars[-1] = "b"
        return "".join(chars)
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# We need the lexicographically smallest non-palindrome after changing exactly
# one character. To make a string smaller, change the earliest possible
# non-'a' character to 'a'. But only the first half matters, because changing a
# mirrored character in the second half would make the string larger than
# changing its matching position in the first half.
#
# Why the fallback works:
# If every character in the first half is 'a', then changing any first-half
# character cannot make the string smaller. The smallest way to break the
# palindrome is to change the last character to 'b'.
#
# Edge cases:
# - Length 1: any one-character string is always a palindrome, so impossible;
#   return an empty string.
# - All 'a's, such as "aaa": return "aab".
# - Odd length: skip the center because changing only the center keeps the
#   string a palindrome.
#
# Complexity:
# - Time: O(n), scan at most half the string and join.
# - Space: O(n), because Python strings are immutable and we build a char list.
