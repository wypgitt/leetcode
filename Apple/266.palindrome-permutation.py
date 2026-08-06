#
# @lc app=leetcode id=266 lang=python3
#
# [266] Palindrome Permutation
#
# https://leetcode.com/problems/palindrome-permutation/description/
#
# algorithms
# Easy (68.69%)
# Likes:    1106
# Dislikes: 75
# Total Accepted:    235.9K
# Total Submissions: 343.4K
# Testcase Example:  "\"code\""
#
#
# Given a string s, return true if a permutation of the string could form
# a palindrome and false otherwise.
#
# Example 1:
#
# Input: s = "code"
# Output: false
#
# Example 2:
#
# Input: s = "aab"
# Output: true
#
# Example 3:
#
# Input: s = "carerac"
# Output: true
#
# Constraints:
#
# 1 <= s.length <= 5000
#
# s consists of only lowercase English letters.
#
# @lc code=start
from collections import Counter


class Solution:
    def canPermutePalindrome(self, s: str) -> bool:
        """
        Interview explanation:
        A permutation is a palindrome iff at most one character has an odd count
        (the optional center).

        Algorithm:
        - Count frequencies; return number of odd counts <= 1.

        Complexity: O(n) time, O(|Σ|) space.
        """
        odd = 0
        for cnt in Counter(s).values():
            if cnt % 2:
                odd += 1
                if odd > 1:
                    return False
        return True
# @lc code=end
