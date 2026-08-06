#
# @lc app=leetcode id=758 lang=python3
#
# [758] Bold Words in String
#
# https://leetcode.com/problems/bold-words-in-string/description/
#
# algorithms
# Medium (52.55%)
# Likes:    282
# Dislikes: 124
# Total Accepted:    20.9K
# Total Submissions: 39.8K
# Testcase Example:  '["ab","bc"]\n"aabcd"'
#
# Given an array of keywords words and a string s, make all appearances of all
# keywords words[i] in s bold. Any letters between <b> and </b> tags become
# bold.
# 
# Return s after adding the bold tags. The returned string should use the least
# number of tags possible, and the tags should form a valid combination.
# 
# 
# Example 1:
# 
# 
# Input: words = ["ab","bc"], s = "aabcd"
# Output: "a<b>abc</b>d"
# Explanation: Note that returning "a<b>a<b>b</b>c</b>d" would use more tags,
# so it is incorrect.
# 
# 
# Example 2:
# 
# 
# Input: words = ["ab","cb"], s = "aabcd"
# Output: "a<b>ab</b>cd"
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 500
# 0 <= words.length <= 50
# 1 <= words[i].length <= 10
# s and words[i] consist of lowercase English letters.
# 
# 
# 
# Note: This question is the same as 616. Add Bold Tag in String.
# 
#

# @lc code=start
from typing import List


class Solution:
    def boldWords(self, words: List[str], s: str) -> str:
        bold = [False] * len(s)
        for word in words:
            start = s.find(word)
            while start != -1:
                for i in range(start, start + len(word)):
                    bold[i] = True
                start = s.find(word, start + 1)

        ans = []
        i = 0
        while i < len(s):
            if not bold[i]:
                ans.append(s[i])
                i += 1
            else:
                ans.append('<b>')
                while i < len(s) and bold[i]:
                    ans.append(s[i])
                    i += 1
                ans.append('</b>')
        return ''.join(ans)
# @lc code=end

"""
Interview explanation:
First mark every character covered by any word occurrence. Then build the output by wrapping each maximal consecutive marked segment in one pair of bold tags. This naturally merges overlapping and adjacent intervals.

Data structure: a boolean array stores coverage per character.

Edge cases: overlapping words and back-to-back words become one bold region. If no characters are marked, the original string is returned.

Complexity: with direct find calls, worst-case time is O(W * occurrences * word_length) plus O(n) output. Space is O(n). A trie could improve matching for larger inputs.
"""
