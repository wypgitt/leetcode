#
# @lc app=leetcode id=848 lang=python3
#
# [848] Shifting Letters
#
# https://leetcode.com/problems/shifting-letters/description/
#
# algorithms
# Medium (46.21%)
# Likes:    1556
# Dislikes: 142
# Total Accepted:    136.9K
# Total Submissions: 296.2K
# Testcase Example:  '"abc"\n[3,5,9]'
#
# You are given a string s of lowercase English letters and an integer array
# shifts of the same length.
# 
# Call the shift() of a letter, the next letter in the alphabet, (wrapping
# around so that 'z' becomes 'a').
# 
# 
# For example, shift('a') = 'b', shift('t') = 'u', and shift('z') = 'a'.
# 
# 
# Now for each shifts[i] = x, we want to shift the first i + 1 letters of s, x
# times.
# 
# Return the final string after all such shifts to s are applied.
# 
# 
# Example 1:
# 
# 
# Input: s = "abc", shifts = [3,5,9]
# Output: "rpl"
# Explanation: We start with "abc".
# After shifting the first 1 letters of s by 3, we have "dbc".
# After shifting the first 2 letters of s by 5, we have "igc".
# After shifting the first 3 letters of s by 9, we have "rpl", the answer.
# 
# 
# Example 2:
# 
# 
# Input: s = "aaa", shifts = [1,2,3]
# Output: "gfd"
# 
# 
# 
# Constraints:
# 
# 
# 1 <= s.length <= 10^5
# s consists of lowercase English letters.
# shifts.length == s.length
# 0 <= shifts[i] <= 10^9
# 
# 
#

# @lc code=start
from typing import List


class Solution:
    def shiftingLetters(self, s: str, shifts: List[int]) -> str:
        chars = list(s)
        total = 0
        for i in range(len(s) - 1, -1, -1):
            total = (total + shifts[i]) % 26
            chars[i] = chr((ord(chars[i]) - ord('a') + total) % 26 + ord('a'))
        return ''.join(chars)
# @lc code=end

"""
Interview explanation:
Character i is affected by shifts[i], shifts[i+1], ..., shifts[n-1]. Scan from right to left while maintaining this suffix sum modulo 26, then shift each character once.

Data structure: mutable character list for the output.

Edge cases: large shift values are reduced modulo 26. Wraparound from 'z' to 'a' is handled by modular arithmetic.

Complexity: O(n) time and O(n) space for the output list.
"""
