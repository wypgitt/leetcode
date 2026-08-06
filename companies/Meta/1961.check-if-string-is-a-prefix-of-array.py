#
# @lc app=leetcode id=1961 lang=python3
#
# [1961] Check If String Is a Prefix of Array
#
# https://leetcode.com/problems/check-if-string-is-a-prefix-of-array/description/
#
# algorithms
# Easy (52.88%)
# Likes:    561
# Dislikes: 110
# Total Accepted:    88.3K
# Total Submissions: 167K
# Testcase Example:  "\"iloveleetcode\""
#
# Given a string s and an array of strings words, determine whether s is a
# prefix string of words.
#
# A string s is a prefix string of words if s can be made by concatenating the
# first k strings in words for some positive k no larger than words.length.
#
# Return true if s is a prefix string of words, or false otherwise.
#
# Example 1:
#
# Input: s = "iloveleetcode", words = ["i","love","leetcode","apples"]
# Output: true
# Explanation:
# s can be made by concatenating "i", "love", and "leetcode" together.
#
# Example 2:
#
# Input: s = "iloveleetcode", words = ["apples","i","love","leetcode"]
# Output: false
# Explanation:
# It is impossible to make s using a prefix of arr.
#
# Constraints:
#
# 1 <= words.length <= 100
#
# 1 <= words[i].length <= 20
#
# 1 <= s.length <= 1000
#
# words[i] and s consist of only lowercase English letters.
#

# @lc code=start
from typing import List


class Solution:
    def isPrefixString(self, s: str, words: List[str]) -> bool:
        """
        Interview explanation:
        Check if s equals concatenation of a non-empty prefix of words.

        Algorithm:
        - Accumulate words until length >= len(s); compare equality.

        Complexity: O(|s|) time, O(|s|) space.
        """
        cur = []
        length = 0
        for w in words:
            cur.append(w)
            length += len(w)
            if length == len(s):
                return "".join(cur) == s
            if length > len(s):
                return False
        return False

    def isPrefixString_pointer(self, s: str, words: List[str]) -> bool:
        """
        Interview explanation:
        Alternate: match s against successive words with an index pointer.

        Algorithm:
        - i=0; for each word, s[i:i+len(w)] must equal w; advance i.
        - Success if i reaches len(s) exactly after some word.

        Complexity: O(|s|) time, O(1) extra space.
        """
        i = 0
        n = len(s)
        for w in words:
            m = len(w)
            if i + m > n or s[i : i + m] != w:
                return False
            i += m
            if i == n:
                return True
        return False
# @lc code=end

