#
# @lc app=leetcode id=383 lang=python3
#
# [383] Ransom Note
#
# https://leetcode.com/problems/ransom-note/description/
#
# algorithms
# Easy (66.27%)
# Likes:    5771
# Dislikes: 549
# Total Accepted:    2.1M
# Total Submissions: 3.1M
# Testcase Example:  "\"a\""
#
# Given two strings ransomNote and magazine, return true if ransomNote can be
# constructed by using the letters from magazine and false otherwise.
#
# Each letter in magazine can only be used once in ransomNote.
#
# Example 1:
#
# Input: ransomNote = "a", magazine = "b"
# Output: false
#
# Example 2:
#
# Input: ransomNote = "aa", magazine = "ab"
# Output: false
#
# Example 3:
#
# Input: ransomNote = "aa", magazine = "aab"
# Output: true
#
# Constraints:
#
# 1 <= ransomNote.length, magazine.length <= 10^5
#
# ransomNote and magazine consist of lowercase English letters.
#

# @lc code=start
from collections import Counter


class Solution:
    def canConstruct(self, ransomNote: str, magazine: str) -> bool:
        """
        Interview explanation:
        Ransom note can be built iff magazine has at least as many of each
        letter. Compare Counter multiplicities (or decrement magazine counts).

        Algorithm:
        - Counter(magazine); for each char in ransomNote, need a remaining count.
        - Or: not (Counter(ransomNote) - Counter(magazine)).

        Complexity: O(m + n) time, O(1) space over alphabet (26 letters).
        """
        need = Counter(ransomNote)
        have = Counter(magazine)
        for ch, cnt in need.items():
            if have[ch] < cnt:
                return False
        return True
# @lc code=end
