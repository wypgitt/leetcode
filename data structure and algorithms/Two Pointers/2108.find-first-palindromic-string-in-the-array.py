#
# @lc app=leetcode id=2108 lang=python3
#
# [2108] Find First Palindromic String in the Array
#
# https://leetcode.com/problems/find-first-palindromic-string-in-the-array/description/
#
# algorithms
# Easy (84.04%)
# Likes:    1672
# Dislikes: 60
# Total Accepted:    401.4K
# Total Submissions: 477.7K
# Testcase Example:  "[\"abc\",\"car\",\"ada\",\"racecar\",\"cool\"]"
#
# Given an array of strings words, return the first palindromic string in the
# array. If there is no such string, return an empty string "".
#
# A string is palindromic if it reads the same forward and backward.
#
#
#
# Example 1:
#
# Input: words = ["abc","car","ada","racecar","cool"]
# Output: "ada"
# Explanation: The first string that is palindromic is "ada".
# Note that "racecar" is also palindromic, but it is not the first.
#
# Example 2:
#
# Input: words = ["notapalindrome","racecar"]
# Output: "racecar"
# Explanation: The first and only string that is palindromic is "racecar".
#
# Example 3:
#
# Input: words = ["def","ghi"]
# Output: ""
# Explanation: There are no palindromic strings, so the empty string is
# returned.
#
#
#
# Constraints:
#
#
# 1 <= words.length <= 100
#
#
# 1 <= words[i].length <= 100
#
#
# words[i] consists only of lowercase English letters.
#


# @lc code=start
from typing import List


class Solution:
    def firstPalindrome(self, words: List[str]) -> str:
        """
        Interview explanation:
        Return the first palindromic string in words, or "" if none.

        Algorithm:
        - Scan left-to-right; return first w where w == w[::-1].

        Complexity: O(total length) time, O(1) extra space.
        """
        for w in words:
            if w == w[::-1]:
                return w
        return ""

    def firstPalindrome_two_pointers(self, words: List[str]) -> str:
        """
        Interview explanation:
        Alternate: check palindrome with two pointers (no reverse copy).

        Algorithm:
        - For each word, L/R pointers until mismatch.

        Complexity: O(total length) time, O(1) space.
        """
        for w in words:
            i, j = 0, len(w) - 1
            ok = True
            while i < j:
                if w[i] != w[j]:
                    ok = False
                    break
                i += 1
                j -= 1
            if ok:
                return w
        return ""
# @lc code=end

