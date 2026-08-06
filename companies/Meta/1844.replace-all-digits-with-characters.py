#
# @lc app=leetcode id=1844 lang=python3
#
# [1844] Replace All Digits with Characters
#
# https://leetcode.com/problems/replace-all-digits-with-characters/description/
#
# algorithms
# Easy (82.88%)
# Likes:    902
# Dislikes: 117
# Total Accepted:    119K
# Total Submissions: 144K
# Testcase Example:  "\"a1c1e1\""
#
# You are given a 0-indexed string s that has lowercase English letters in its
# even indices and digits in its odd indices.
#
# You must perform an operation shift(c, x), where c is a character and x is a
# digit, that returns the x^th character after c.
#
# For example, shift('a', 5) = 'f' and shift('x', 0) = 'x'.
#
# For every odd index i, you want to replace the digit s[i] with the result of
# the shift(s[i-1], s[i]) operation.
#
# Return s after replacing all digits. It is guaranteed that shift(s[i-1],
# s[i]) will never exceed 'z'.
#
# Note that shift(c, x) is not a preloaded function, but an operation to be
# implemented as part of the solution.
#
# Example 1:
#
# Input: s = "a1c1e1"
# Output: "abcdef"
# Explanation: The digits are replaced as follows:
# - s[1] -> shift('a',1) = 'b'
# - s[3] -> shift('c',1) = 'd'
# - s[5] -> shift('e',1) = 'f'
#
# Example 2:
#
# Input: s = "a1b2c3d4e"
# Output: "abbdcfdhe"
# Explanation: The digits are replaced as follows:
# - s[1] -> shift('a',1) = 'b'
# - s[3] -> shift('b',2) = 'd'
# - s[5] -> shift('c',3) = 'f'
# - s[7] -> shift('d',4) = 'h'
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists only of lowercase English letters and digits.
#
# shift(s[i-1], s[i]) <= 'z' for all odd indices i.
#

# @lc code=start
class Solution:
    def replaceDigits(self, s: str) -> str:
        """
        Interview explanation:
        Odd indices are digits: replace s[i] with shift(s[i-1], int(s[i])).

        Algorithm (scan):
        - Build list; for odd i set chr(ord(prev)+digit).

        Complexity: O(n) time, O(n) space.
        """
        chars = list(s)
        for i in range(1, len(chars), 2):
            chars[i] = chr(ord(chars[i - 1]) + int(chars[i]))
        return ''.join(chars)
# @lc code=end
