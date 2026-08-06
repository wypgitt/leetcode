#
# @lc app=leetcode id=2423 lang=python3
#
# [2423] Remove Letter To Equalize Frequency
#
# https://leetcode.com/problems/remove-letter-to-equalize-frequency/description/
#
# algorithms
# Easy (19.54%)
# Likes:    814
# Dislikes: 1368
# Total Accepted:    79.5K
# Total Submissions: 407K
# Testcase Example:  "\"abcc\""
#
# You are given a 0-indexed string word, consisting of lowercase English
# letters. You need to select one index and remove the letter at that index from
# word so that the frequency of every letter present in word is equal.
#
# Return true if it is possible to remove one letter so that the frequency of
# all letters in word are equal, and false otherwise.
#
# Note:
#
#
# The frequency of a letter x is the number of times it occurs in the string.
#
#
# You must remove exactly one letter and cannot choose to do nothing.
#
#
#
# Example 1:
#
# Input: word = "abcc"
# Output: true
# Explanation: Select index 3 and delete it: word becomes "abc" and each
# character has a frequency of 1.
#
# Example 2:
#
# Input: word = "aazz"
# Output: false
# Explanation: We must delete a character, so either the frequency of "a" is 1
# and the frequency of "z" is 2, or vice versa. It is impossible to make all
# present letters have equal frequency.
#
#
#
# Constraints:
#
#
# 2 <= word.length <= 100
#
#
# word consists of lowercase English letters only.
#

# @lc code=start
from collections import Counter


class Solution:
    def equalFrequency(self, word: str) -> bool:
        """
        Interview explanation:
        Return true if deleting exactly one letter occurrence makes all remaining
        letter frequencies equal.

        Algorithm:
        - Try decrementing each distinct character's count once; check remaining
          positive freqs are all equal.

        Complexity: O(26^2) = O(1) time, O(1) space.
        """
        cnt = Counter(word)
        for ch in list(cnt):
            cnt[ch] -= 1
            freqs = [v for v in cnt.values() if v > 0]
            if freqs and len(set(freqs)) == 1:
                return True
            cnt[ch] += 1
        return False
# @lc code=end
