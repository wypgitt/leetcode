#
# @lc app=leetcode id=3174 lang=python3
#
# [3174] Clear Digits
#
# https://leetcode.com/problems/clear-digits/description/
#
# algorithms
# Easy (82.85%)
# Likes:    717
# Dislikes: 28
# Total Accepted:    291.1K
# Total Submissions: 351.3K
# Testcase Example:  "\"abc\""
#
#
# You are given a string s.
#
# Your task is to remove all digits by doing this operation repeatedly:
#
# Delete the first digit and the closest non-digit character to its left.
#
# Return the resulting string after removing all digits.
#
# Note that the operation cannot be performed on a digit that does not
# have any non-digit character to its left.
#
# Example 1:
#
# Input: s = "abc"
#
# Output: "abc"
#
# Explanation:
#
# There is no digit in the string.
#
# Example 2:
#
# Input: s = "cb34"
#
# Output: ""
#
# Explanation:
#
# First, we apply the operation on s[2], and s becomes "c4".
#
# Then we apply the operation on s[1], and s becomes "".
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s consists only of lowercase English letters and digits.
#
# The input is generated such that it is possible to delete all digits.
#

# @lc code=start
class Solution:
    def clearDigits(self, s: str) -> str:
        """
        Interview explanation:
        Each digit deletes the closest non-digit to its left — classic stack
        cancellation of letter/digit pairs.

        Algorithm:
        - Push letters; on a digit, pop the stack (guaranteed non-empty).

        Complexity: O(n) time, O(n) space.
        """
        stack: list[str] = []
        for c in s:
            if c.isdigit():
                stack.pop()
            else:
                stack.append(c)
        return "".join(stack)

    def clearDigits_two_pointer(self, s: str) -> str:
        """
        Interview explanation:
        Alternate: in-place style with a write pointer over a list buffer.

        Algorithm:
        - Write letters forward; on digit, decrement write pointer.

        Complexity: O(n) time, O(n) space.
        """
        buf = list(s)
        w = 0
        for c in buf:
            if c.isdigit():
                w -= 1
            else:
                buf[w] = c
                w += 1
        return "".join(buf[:w])
# @lc code=end
