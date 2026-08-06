#
# @lc app=leetcode id=3775 lang=python3
#
# [3775] Reverse Words With Same Vowel Count
#
# https://leetcode.com/problems/reverse-words-with-same-vowel-count/description/
#
# algorithms
# Medium (67.08%)
# Likes:    59
# Dislikes: 9
# Total Accepted:    38.7K
# Total Submissions: 57.7K
# Testcase Example:  "\"cat and mice\""
#
#
# You are given a string s consisting of lowercase English words, each
# separated by a single space.
#
# Determine how many vowels appear in the first word. Then, reverse each
# following word that has the same vowel count. Leave all remaining words
# unchanged.
#
# Return the resulting string.
#
# Vowels are 'a', 'e', 'i', 'o', and 'u'.
#
# Example 1:
#
# Input: s = "cat and mice"
#
# Output: "cat dna mice"
#
# Explanation:​​​​​​​
#
# The first word "cat" has 1 vowel.
#
# "and" has 1 vowel, so it is reversed to form "dna".
#
# "mice" has 2 vowels, so it remains unchanged.
#
# Thus, the resulting string is "cat dna mice".
#
# Example 2:
#
# Input: s = "book is nice"
#
# Output: "book is ecin"
#
# Explanation:
#
# The first word "book" has 2 vowels.
#
# "is" has 1 vowel, so it remains unchanged.
#
# "nice" has 2 vowels, so it is reversed to form "ecin".
#
# Thus, the resulting string is "book is ecin".
#
# Example 3:
#
# Input: s = "banana healthy"
#
# Output: "banana healthy"
#
# Explanation:
#
# The first word "banana" has 3 vowels.
#
# "healthy" has 2 vowels, so it remains unchanged.
#
# Thus, the resulting string is "banana healthy".
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s consists of lowercase English letters and spaces.
#
# Words in s are separated by a single space.
#
# s does not contain leading or trailing spaces.
#

# @lc code=start
class Solution:
    def reverseWords(self, s: str) -> str:
        """
        Interview explanation:
        Count vowels in the first word; reverse later words with the same count.

        Algorithm:
        - Split on spaces; target = vowel_count(words[0]); reverse matching tails.

        Complexity: O(n) time, O(n) space.
        """
        vowels = set("aeiou")

        def vowel_count(w: str) -> int:
            return sum(ch in vowels for ch in w)

        words = s.split(" ")
        target = vowel_count(words[0])
        for i in range(1, len(words)):
            if vowel_count(words[i]) == target:
                words[i] = words[i][::-1]
        return " ".join(words)
# @lc code=end
