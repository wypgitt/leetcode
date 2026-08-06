#
# @lc app=leetcode id=3856 lang=python3
#
# [3856] Trim Trailing Vowels
#
# https://leetcode.com/problems/trim-trailing-vowels/description/
#
# algorithms
# Easy (77.63%)
# Likes:    41
# Dislikes: 0
# Total Accepted:    59.9K
# Total Submissions: 77.1K
# Testcase Example:  "\"idea\""
#
#
# You are given a string s that consists of lowercase English letters.
#
# Return the string obtained by removing all trailing vowels from s.
#
# The vowels consist of the characters 'a', 'e', 'i', 'o', and 'u'.
#
# Example 1:
#
# Input: s = "idea"
#
# Output: "id"
#
# Explanation:
#
# Removing "idea", we obtain the string "id".
#
# Example 2:
#
# Input: s = "day"
#
# Output: "day"
#
# Explanation:
#
# There are no trailing vowels in the string "day".
#
# Example 3:
#
# Input: s = "aeiou"
#
# Output: ""
#
# Explanation:
#
# Removing "aeiou", we obtain the string "".
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists of only lowercase English letters.
#

# @lc code=start
class Solution:
    def trimTrailingVowels(self, s: str) -> str:
        """
        Interview explanation:
        Strip vowels from the end until a consonant (or empty) remains.

        Algorithm:
        - Walk from the right while characters are in {a,e,i,o,u}.
        - Return the untrimmed prefix.

        Complexity: O(n) time, O(1) extra space (slice may copy).
        """
        vowels = set("aeiou")
        i = len(s)
        while i > 0 and s[i - 1] in vowels:
            i -= 1
        return s[:i]

    def trimTrailingVowels_rstrip(self, s: str) -> str:
        """
        Interview explanation:
        Alternate: use rstrip with the vowel alphabet.

        Algorithm:
        - return s.rstrip("aeiou").

        Complexity: O(n) time, O(n) space for the result.
        """
        return s.rstrip("aeiou")
# @lc code=end
