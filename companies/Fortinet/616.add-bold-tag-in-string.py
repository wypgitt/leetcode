#
# @lc app=leetcode id=616 lang=python3
#
# [616] Add Bold Tag in String
#
# https://leetcode.com/problems/add-bold-tag-in-string/description/
#
# algorithms
# Medium (51.50%)
# Likes:    1117
# Dislikes: 204
# Total Accepted:    106.3K
# Total Submissions: 206.5K
# Testcase Example:  "\"abcxyz123\"\n[\"abc\",\"123\"]"
#
#
# You are given a string s and an array of strings words.
#
# You should add a closed pair of bold tag <b> and </b> to wrap the
# substrings in s that exist in words.
#
# If two such substrings overlap, you should wrap them together with only
# one pair of closed bold-tag.
#
# If two substrings wrapped by bold tags are consecutive, you should
# combine them.
#
# Return s after adding the bold tags.
#
# Example 1:
#
# Input: s = "abcxyz123", words = ["abc","123"]
# Output: "<b>abc</b>xyz<b>123</b>"
# Explanation: The two strings of words are substrings of s as following:
# "abcxyz123".
# We add <b> before each substring and </b> after each substring.
#
# Example 2:
#
# Input: s = "aaabbb", words = ["aa","b"]
# Output: "<b>aaabbb</b>"
# Explanation:
# "aa" appears as a substring two times: "aaabbb" and "aaabbb".
# "b" appears as a substring three times: "aaabbb", "aaabbb", and
# "aaabbb".
# We add <b> before each substring and </b> after each substring:
# "<b>a<b>a</b>a</b><b>b</b><b>b</b><b>b</b>".
# Since the first two <b>'s overlap, we merge them:
# "<b>aaa</b><b>b</b><b>b</b><b>b</b>".
# Since now the four <b>'s are consecutive, we merge them:
# "<b>aaabbb</b>".
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# 0 <= words.length <= 100
#
# 1 <= words[i].length <= 1000
#
# s and words[i] consist of English letters and digits.
#
# All the values of words are unique.
#
# Note: This question is the same as 758. Bold Words in String.
#
# @lc code=start

from typing import List


class Solution:
    def addBoldTag(self, s: str, words: List[str]) -> str:
        """
        Interview explanation:
        Premium. Mark every substring of s that equals any word in words, merge
        overlapping/adjacent marked ranges, wrap with <b></b>.

        Algorithm:
        - Boolean mask bold[i] for characters covered by some word match.
        - For each word, find all occurrences (or KMP/trie) and mark ranges.
        - Scan mask: open <b> on rising edge, close </b> on falling edge.

        Complexity: O(N * W * L) naive match (N=|s|, W=#words, L=avg len); O(N) space.
        """
        n = len(s)
        bold = [False] * n
        for w in words:
            start = s.find(w)
            while start != -1:
                for i in range(start, start + len(w)):
                    bold[i] = True
                start = s.find(w, start + 1)
        res = []
        i = 0
        while i < n:
            if bold[i]:
                res.append("<b>")
                while i < n and bold[i]:
                    res.append(s[i])
                    i += 1
                res.append("</b>")
            else:
                res.append(s[i])
                i += 1
        return "".join(res)
# @lc code=end
