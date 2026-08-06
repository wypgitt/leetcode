#
# @lc app=leetcode id=1933 lang=python3
#
# [1933] Check if String Is Decomposable Into Value-Equal Substrings
#
# https://leetcode.com/problems/check-if-string-is-decomposable-into-value-equal-substrings/description/
#
# algorithms
# Easy (51.03%)
# Likes:    61
# Dislikes: 15
# Total Accepted:    4.9K
# Total Submissions: 9.5K
# Testcase Example:  "\"000111000\""
#
#
# A value-equal string is a string where all characters are the same.
#
# For example, "1111" and "33" are value-equal strings.
#
# In contrast, "123" is not a value-equal string.
#
# Given a digit string s, decompose the string into some number of
# consecutive value-equal substrings where exactly one substring has a
# length of 2 and the remaining substrings have a length of 3.
#
# Return true if you can decompose s according to the above rules.
# Otherwise, return false.
#
# A substring is a contiguous sequence of characters in a string.
#
# Example 1:
#
# Input: s = "000111000"
# Output: false
# Explanation: s cannot be decomposed according to the rules because
# ["000", "111", "000"] does not have a substring of length 2.
#
# Example 2:
#
# Input: s = "00011111222"
# Output: true
# Explanation: s can be decomposed into ["000", "111", "11", "222"].
#
# Example 3:
#
# Input: s = "011100022233"
# Output: false
# Explanation: s cannot be decomposed according to the rules because of
# the first '0'.
#
# Constraints:
#
# 1 <= s.length <= 1000
#
# s consists of only digits '0' through '9'.
#
# @lc code=start
class Solution:
    def isDecomposable(self, s: str) -> bool:
        """
        Interview explanation:
        Premium. Decompose s into contiguous groups of identical chars of length
        2 or 3, with exactly one group of length 2 (rest length 3).

        Algorithm:
        - Run-length encode. Each run length L must be L%3==0 or L%3==2.
          Exactly one run contributes a remainder-2 (the single length-2 group);
          others fully groups of 3. Total: exactly one '2' used.

        Complexity: O(n) time, O(1) space.
        """
        twos = 0
        i, n = 0, len(s)
        while i < n:
            j = i
            while j < n and s[j] == s[i]:
                j += 1
            L = j - i
            if L % 3 == 1:
                return False
            if L % 3 == 2:
                twos += 1
                if twos > 1:
                    return False
            i = j
        return twos == 1
# @lc code=end
