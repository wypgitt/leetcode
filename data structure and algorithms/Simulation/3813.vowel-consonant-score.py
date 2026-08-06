#
# @lc app=leetcode id=3813 lang=python3
#
# [3813] Vowel-Consonant Score
#
# https://leetcode.com/problems/vowel-consonant-score/description/
#
# algorithms
# Easy (53.81%)
# Likes:    54
# Dislikes: 4
# Total Accepted:    52.8K
# Total Submissions: 98.2K
# Testcase Example:  "\"cooear\""
#
#
# You are given a string s consisting of lowercase English letters,
# spaces, and digits.
#
# Let v be the number of vowels in s and c be the number of consonants in
# s.
#
# A vowel is one of the letters 'a', 'e', 'i', 'o', or 'u', while any
# other letter in the English alphabet is considered a consonant.
#
# The score of the string s is defined as follows:
#
# If c > 0, the score = floor(v / c) where floor denotes rounding down to
# the nearest integer.
#
# Otherwise, the score = 0.
#
# Return an integer denoting the score of the string.
#
# Example 1:
#
# Input: s = "cooear"
#
# Output: 2
#
# Explanation:
#
# The string s = "cooear" contains v = 4 vowels ('o', 'o', 'e', 'a') and c
# = 2 consonants ('c', 'r').
#
# The score is floor(v / c) = floor(4 / 2) = 2.
#
# Example 2:
#
# Input: s = "axeyizou"
#
# Output: 1
#
# Explanation:
#
# The string s = "axeyizou" contains v = 5 vowels ('a', 'e', 'i', 'o',
# 'u') and c = 3 consonants ('x', 'y', 'z').
#
# The score is floor(v / c) = floor(5 / 3) = 1.
#
# Example 3:
#
# Input: s = "au 123"
#
# Output: 0
#
# Explanation:
#
# The string s = "au 123" contains no consonants (c = 0), so the score is
# 0.
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists of lowercase English letters, spaces and digits.
#

# @lc code=start

class Solution:
    def vowelConsonantScore(self, s: str) -> int:
        """
        Interview explanation:
        Score is floor(vowels / consonants) over letters only; 0 if no
        consonants.

        Algorithm:
        - Count vowels aeiou and other letters as consonants; ignore digits
          and spaces. Return v // c if c > 0 else 0.

        Complexity: O(n) time, O(1) space.
        """
        vowels = set("aeiou")
        v = c = 0
        for ch in s:
            if "a" <= ch <= "z":
                if ch in vowels:
                    v += 1
                else:
                    c += 1
        return v // c if c else 0
# @lc code=end
