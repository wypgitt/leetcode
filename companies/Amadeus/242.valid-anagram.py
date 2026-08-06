#
# @lc app=leetcode id=242 lang=python3
#
# [242] Valid Anagram
#
# https://leetcode.com/problems/valid-anagram/description/
#
# algorithms
# Easy (68.48%)
# Likes:    14587
# Dislikes: 482
# Total Accepted:    6.6M
# Total Submissions: 9.6M
# Testcase Example:  "\"anagram\""
#
# Given two strings s and t, return true if t is an anagram of s, and false
# otherwise.
#
# Example 1:
#
# Input: s = "anagram", t = "nagaram"
#
# Output: true
#
# Example 2:
#
# Input: s = "rat", t = "car"
#
# Output: false
#
# Constraints:
#
# 1 <= s.length, t.length <= 5 * 10^4
#
# s and t consist of lowercase English letters.
#
# Follow up: What if the inputs contain Unicode characters? How would you adapt
# your solution to such a case?
#

# @lc code=start
from collections import Counter


class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        """
        Interview explanation:
        Anagrams have identical character counts. Compare Counter(s) and Counter(t)
        (works for Unicode too).

        Algorithm:
        - Early length check; return Counter(s) == Counter(t).

        Complexity: O(n) time, O(|Σ|) space.
        """
        if len(s) != len(t):
            return False
        return Counter(s) == Counter(t)
# @lc code=end
