#
# @lc app=leetcode id=30 lang=python3
#
# [30] Substring with Concatenation of All Words
#
# https://leetcode.com/problems/substring-with-concatenation-of-all-words/description/
#
# algorithms
# Hard (34.91%)
# Likes:    2737
# Dislikes: 445
# Total Accepted:    754K
# Total Submissions: 2.2M
# Testcase Example:  "\"barfoothefoobarman\""
#
# You are given a string s and an array of strings words. All the strings of
# words are of the same length.
#
# A concatenated string is a string that exactly contains all the strings of
# any permutation of words concatenated.
#
# For example, if words = ["ab","cd","ef"], then "abcdef", "abefcd", "cdabef",
# "cdefab", "efabcd", and "efcdab" are all concatenated strings. "acdbef" is
# not a concatenated string because it is not the concatenation of any
# permutation of words.
#
# Return an array of the starting indices of all the concatenated substrings in
# s. You can return the answer in any order.
#
# Example 1:
#
# Input: s = "barfoothefoobarman", words = ["foo","bar"]
#
# Output: [0,9]
#
# Explanation:
#
# The substring starting at 0 is "barfoo". It is the concatenation of
# ["bar","foo"] which is a permutation of words.
#
# The substring starting at 9 is "foobar". It is the concatenation of
# ["foo","bar"] which is a permutation of words.
#
# Example 2:
#
# Input: s = "wordgoodgoodgoodbestword", words = ["word","good","best","word"]
#
# Output: []
#
# Explanation:
#
# There is no concatenated substring.
#
# Example 3:
#
# Input: s = "barfoofoobarthefoobarman", words = ["bar","foo","the"]
#
# Output: [6,9,12]
#
# Explanation:
#
# The substring starting at 6 is "foobarthe". It is the concatenation of
# ["foo","bar","the"].
#
# The substring starting at 9 is "barthefoo". It is the concatenation of
# ["bar","the","foo"].
#
# The substring starting at 12 is "thefoobar". It is the concatenation of
# ["the","foo","bar"].
#
# Constraints:
#
# 1 <= s.length <= 10^4
#
# 1 <= words.length <= 5000
#
# 1 <= words[i].length <= 30
#
# s and words[i] consist of lowercase English letters.
#

# @lc code=start
from collections import Counter
from typing import List


class Solution:
    def findSubstring(self, s: str, words: List[str]) -> List[int]:
        """
        Interview explanation:
        All words have equal length w, so a valid concatenation is a window of
        len(words)*w formed by exactly the multiset of words. Slide word-sized
        steps for each residue class mod w.

        Algorithm:
        - Build need = Counter(words).
        - For each offset r in [0, w):
          - Maintain a sliding window of word chunks with a running Counter.
          - Expand by one word; if a word is excess/unknown, shrink from left.
          - When window holds exactly word_count words and matches need, record
            the start index.

        Complexity: O(n * w) time with hashmap operations amortized O(1) per
        word step for fixed alphabets/short keys; O(k) space for counters
        (k = number of distinct words).
        """
        if not s or not words:
            return []

        word_len = len(words[0])
        word_count = len(words)
        total_len = word_len * word_count
        n = len(s)
        if n < total_len:
            return []

        need = Counter(words)
        ans = []

        for offset in range(word_len):
            left = offset
            seen: Counter[str] = Counter()
            count = 0

            for right in range(offset, n - word_len + 1, word_len):
                word = s[right : right + word_len]
                if word in need:
                    seen[word] += 1
                    count += 1
                    while seen[word] > need[word]:
                        left_word = s[left : left + word_len]
                        seen[left_word] -= 1
                        left += word_len
                        count -= 1
                    if count == word_count:
                        ans.append(left)
                else:
                    seen.clear()
                    count = 0
                    left = right + word_len

        return ans
# @lc code=end
