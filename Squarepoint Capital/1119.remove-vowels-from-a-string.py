#
# @lc app=leetcode id=1119 lang=python3
#
# [1119] Remove Vowels from a String
#
# https://leetcode.com/problems/remove-vowels-from-a-string/description/
#
# algorithms
# Easy (91.29%)
# Likes:    368
# Dislikes: 116
# Total Accepted:    118.5K
# Total Submissions: 129.8K
# Testcase Example:  "\"leetcodeisacommunityforcoders\""
#
#
# Given a string s, remove the vowels 'a', 'e', 'i', 'o', and 'u' from it,
# and return the new string.
#
# Example 1:
#
# Input: s = "leetcodeisacommunityforcoders"
# Output: "ltcdscmmntyfrcdrs"
#
# Example 2:
#
# Input: s = "aeiou"
# Output: ""
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s consists of only lowercase English letters.
#
# @lc code=start
class Solution:
    def removeVowels(self, s: str) -> str:
        """
        Interview explanation:
        Premium. Remove all vowels aeiou from s (lowercase).

        Algorithm:
        - Filter characters not in vowel set; join.

        Complexity: O(n) time/space.
        """
        vowels = set("aeiou")
        return "".join(c for c in s if c not in vowels)
# @lc code=end
