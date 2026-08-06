#
# @lc app=leetcode id=1160 lang=python3
#
# [1160] Find Words That Can Be Formed by Characters
#
# https://leetcode.com/problems/find-words-that-can-be-formed-by-characters/description/
#
# algorithms
# Easy (71.71%)
# Likes:    2272
# Dislikes: 190
# Total Accepted:    341K
# Total Submissions: 476K
# Testcase Example:  "[\"cat\",\"bt\",\"hat\",\"tree\"]"
#
# You are given an array of strings words and a string chars.
#
# A string is good if it can be formed by characters from chars (each character
# can only be used once for each word in words).
#
# Return the sum of lengths of all good strings in words.
#
# Example 1:
#
# Input: words = ["cat","bt","hat","tree"], chars = "atach"
# Output: 6
# Explanation: The strings that can be formed are "cat" and "hat" so the answer
# is 3 + 3 = 6.
#
# Example 2:
#
# Input: words = ["hello","world","leetcode"], chars = "welldonehoneyr"
# Output: 10
# Explanation: The strings that can be formed are "hello" and "world" so the
# answer is 5 + 5 = 10.
#
# Constraints:
#
# 1 <= words.length <= 1000
#
# 1 <= words[i].length, chars.length <= 100
#
# words[i] and chars consist of lowercase English letters.
#

# @lc code=start
from typing import List
from collections import Counter


class Solution:
    def countCharacters(self, words: List[str], chars: str) -> int:
        """
        Interview explanation:
        Sum lengths of words that can be formed from chars (each char used at
        most its frequency in chars).

        Algorithm:
        - Counter(chars); for each word, if Counter(word) <= avail, add len.

        Complexity: O(total characters) time, O(1) alphabet space.
        """
        avail = Counter(chars)
        ans = 0
        for w in words:
            need = Counter(w)
            if all(need[c] <= avail[c] for c in need):
                ans += len(w)
        return ans
# @lc code=end
