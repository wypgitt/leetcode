#
# @lc app=leetcode id=3136 lang=python3
#
# [3136] Valid Word
#
# https://leetcode.com/problems/valid-word/description/
#
# algorithms
# Easy (50.93%)
# Likes:    488
# Dislikes: 170
# Total Accepted:    212.3K
# Total Submissions: 416.8K
# Testcase Example:  "\"234Adas\""
#
#
# A word is considered valid if:
#
# It contains a minimum of 3 characters.
#
# It contains only digits (0-9), and English letters (uppercase and
# lowercase).
#
# It includes at least one vowel.
#
# It includes at least one consonant.
#
# You are given a string word.
#
# Return true if word is valid, otherwise, return false.
#
# Notes:
#
# 'a', 'e', 'i', 'o', 'u', and their uppercases are vowels.
#
# A consonant is an English letter that is not a vowel.
#
# Example 1:
#
# Input: word = "234Adas"
#
# Output: true
#
# Explanation:
#
# This word satisfies the conditions.
#
# Example 2:
#
# Input: word = "b3"
#
# Output: false
#
# Explanation:
#
# The length of this word is fewer than 3, and does not have a vowel.
#
# Example 3:
#
# Input: word = "a3$e"
#
# Output: false
#
# Explanation:
#
# This word contains a '$' character and does not have a consonant.
#
# Constraints:
#
# 1 <= word.length <= 20
#
# word consists of English uppercase and lowercase letters, digits, '@',
# '#', and '$'.
#

# @lc code=start
class Solution:
    def isValid(self, word: str) -> bool:
        """
        Interview explanation:
        A valid word has length >= 3, only alphanumerics, at least one vowel,
        and at least one consonant.

        Algorithm:
        - Scan characters: reject non-alphanumeric; track vowel/consonant flags
          among letters (vowels aeiou case-insensitive).

        Complexity: O(n) time, O(1) space.
        """
        if len(word) < 3:
            return False
        vowels = set("aeiouAEIOU")
        has_vowel = False
        has_consonant = False
        for ch in word:
            if ch.isdigit():
                continue
            if ch.isalpha():
                if ch in vowels:
                    has_vowel = True
                else:
                    has_consonant = True
            else:
                return False
        return has_vowel and has_consonant
# @lc code=end
