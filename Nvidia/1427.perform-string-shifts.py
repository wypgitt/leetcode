#
# @lc app=leetcode id=1427 lang=python3
#
# [1427] Perform String Shifts
#
# https://leetcode.com/problems/perform-string-shifts/description/
#
# algorithms
# Easy (55.99%)
# Likes:    277
# Dislikes: 16
# Total Accepted:    94.6K
# Total Submissions: 169K
# Testcase Example:  "\"abc\"\n[[0,1],[1,2]]"
#
#
# You are given a string s containing lowercase English letters, and a
# matrix shift, where shift[i] = [direction_i, amount_i]:
#
# direction_i can be 0 (for left shift) or 1 (for right shift).
#
# amount_i is the amount by which string s is to be shifted.
#
# A left shift by 1 means remove the first character of s and append it to
# the end.
#
# Similarly, a right shift by 1 means remove the last character of s and
# add it to the beginning.
#
# Return the final string after all operations.
#
# Example 1:
#
# Input: s = "abc", shift = [[0,1],[1,2]]
# Output: "cab"
# Explanation:
# [0,1] means shift to left by 1. "abc" -> "bca"
# [1,2] means shift to right by 2. "bca" -> "cab"
#
# Example 2:
#
# Input: s = "abcdefg", shift = [[1,1],[1,1],[0,2],[1,3]]
# Output: "efgabcd"
# Explanation:
# [1,1] means shift to right by 1. "abcdefg" -> "gabcdef"
# [1,1] means shift to right by 1. "gabcdef" -> "fgabcde"
# [0,2] means shift to left by 2. "fgabcde" -> "abcdefg"
# [1,3] means shift to right by 3. "abcdefg" -> "efgabcd"
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s only contains lower case English letters.
#
# 1 <= shift.length <= 100
#
# shift[i].length == 2
#
# direction_i_ is either 0 or 1.
#
# 0 <= amount_i <= 100
#
# @lc code=start
from typing import List


class Solution:
    def stringShift(self, s: str, shift: List[List[int]]) -> str:
        """
        Interview explanation:
        Premium. shift[i]=[direction, amount]: 0=left, 1=right. Net all shifts
        into one rotation modulo n.

        Algorithm:
        (net rotation)
        - net = sum(+amt for right, -amt for left) % n; return s[-net:]+s[:-net]
          (positive net = right rotate).

        Complexity: O(n + |shift|) time, O(n) space.
        """
        n = len(s)
        net = 0
        for d, amt in shift:
            net += amt if d == 1 else -amt
        net %= n
        if net == 0:
            return s
        return s[-net:] + s[:-net]

    def stringShift_simulate(self, s: str, shift: List[List[int]]) -> str:
        """
        Interview explanation:
        Alternate: apply each shift sequentially (clear but slower).

        Algorithm:
        - For each op rotate string by amt % n.

        Complexity: O(n * |shift|) time, O(n) space.
        """
        chars = list(s)
        n = len(chars)
        for d, amt in shift:
            amt %= n
            if amt == 0:
                continue
            if d == 0:  # left
                chars = chars[amt:] + chars[:amt]
            else:
                chars = chars[-amt:] + chars[:-amt]
        return "".join(chars)
# @lc code=end
