#
# @lc app=leetcode id=3913 lang=python3
#
# [3913] Sort Vowels by Frequency
#
# https://leetcode.com/problems/sort-vowels-by-frequency/description/
#
# algorithms
# Medium (62.92%)
# Likes:    53
# Dislikes: 4
# Total Accepted:    27.9K
# Total Submissions: 44.3K
# Testcase Example:  "\"leetcode\""
#
#
# You are given a string s consisting of lowercase English characters.
#
# Rearrange only the vowels in the string so that they appear in
# non-increasing order of their frequency.
#
# If multiple vowels have the same frequency, order them by the position
# of their first occurrence in s.
#
# Return the modified string.
#
# Vowels are 'a', 'e', 'i', 'o', and 'u'.
#
# The frequency of a letter is the number of times it occurs in the
# string.
#
# Example 1:
#
# Input: s = "leetcode"
#
# Output: "leetcedo"
#
# Explanation:​​​​​​​
#
# Vowels in the string are ['e', 'e', 'o', 'e'] with frequencies: e = 3, o
# = 1.
#
# Sorting in non-increasing order of frequency and placing them back into
# the vowel positions results in "leetcedo".
#
# Example 2:
#
# Input: s = "aeiaaioooa"
#
# Output: "aaaaoooiie"
#
# Explanation:​​​​​​​
#
# Vowels in the string are ['a', 'e', 'i', 'a', 'a', 'i', 'o', 'o', 'o',
# 'a'] with frequencies: a = 4, o = 3, i = 2, e = 1.
#
# Sorting them in non-increasing order of frequency and placing them back
# into the vowel positions results in "aaaaoooiie".
#
# Example 3:
#
# Input: s = "baeiou"
#
# Output: "baeiou"
#
# Explanation:
#
# Each vowel appears exactly once, so all have the same frequency.
#
# Thus, they retain their relative order based on first occurrence, and
# the string remains unchanged.
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of lowercase English letters
#

# @lc code=start
from collections import Counter


class Solution:
    def sortVowels(self, s: str) -> str:
        """
        Interview explanation:
        Reorder only vowels by non-increasing frequency; ties keep first-seen
        order. Consonants stay fixed.

        Algorithm:
        - Count vowel frequencies and first occurrence indices.
        - Sort unique vowels by (-freq, first_index); expand into a stream.
        - Rewrite vowel positions left to right from that stream.

        Complexity: O(n) time, O(n) space.
        """
        vowels = set("aeiou")
        count = Counter()
        first = {}

        for index, ch in enumerate(s):
            if ch in vowels:
                count[ch] += 1
                if ch not in first:
                    first[ch] = index

        ordered_vowels = sorted(count, key=lambda ch: (-count[ch], first[ch]))
        sorted_stream = []
        for ch in ordered_vowels:
            sorted_stream.extend(ch for _ in range(count[ch]))

        chars = list(s)
        stream_index = 0
        for index, ch in enumerate(chars):
            if ch in vowels:
                chars[index] = sorted_stream[stream_index]
                stream_index += 1

        return "".join(chars)
# @lc code=end
