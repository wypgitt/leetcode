#
# @lc app=leetcode id=344 lang=python3
#
# [344] Reverse String
#
# https://leetcode.com/problems/reverse-string/description/
#
# algorithms
# Easy (81.14%)
# Likes:    9707
# Dislikes: 1217
# Total Accepted:    4.0M
# Total Submissions: 5.0M
# Testcase Example:  "[\"h\",\"e\",\"l\",\"l\",\"o\"]"
#
# Write a function that reverses a string. The input string is given as an
# array of characters s.
#
# You must do this by modifying the input array in-place with O(1) extra
# memory.
#
# Example 1:
#
# Input: s = ["h","e","l","l","o"]
# Output: ["o","l","l","e","h"]
#
# Example 2:
#
# Input: s = ["H","a","n","n","a","h"]
# Output: ["h","a","n","n","a","H"]
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is a printable ascii character.
#

# @lc code=start
from typing import List


class Solution:
    def reverseString(self, s: List[str]) -> None:
        """
        Interview explanation:
        Two pointers from ends swap toward the center until they meet.

        Algorithm:
        - left, right = 0, n-1; while left < right: swap and move inward.

        Complexity: O(n) time, O(1) space.
        Do not return anything, modify s in-place instead.
        """
        left, right = 0, len(s) - 1
        while left < right:
            s[left], s[right] = s[right], s[left]
            left += 1
            right -= 1
# @lc code=end
