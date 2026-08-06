#
# @lc app=leetcode id=20 lang=python3
#
# [20] Valid Parentheses
#
# https://leetcode.com/problems/valid-parentheses/description/
#
# algorithms
# Easy (44.66%)
# Likes:    28272
# Dislikes: 2023
# Total Accepted:    8.0M
# Total Submissions: 18M
# Testcase Example:  "\"()\""
#
# Given a string s containing just the characters '(', ')', '{', '}', '[' and
# ']', determine if the input string is valid.
#
# An input string is valid if:
#
# Open brackets must be closed by the same type of brackets.
#
# Open brackets must be closed in the correct order.
#
# Every close bracket has a corresponding open bracket of the same type.
#
# Example 1:
#
# Input: s = "()"
#
# Output: true
#
# Example 2:
#
# Input: s = "()[]{}"
#
# Output: true
#
# Example 3:
#
# Input: s = "(]"
#
# Output: false
#
# Example 4:
#
# Input: s = "([])"
#
# Output: true
#
# Example 5:
#
# Input: s = "([)]"
#
# Output: false
#
# Constraints:
#
# 1 <= s.length <= 10^4
#
# s consists of parentheses only '()[]{}'.
#

# @lc code=start
class Solution:
    def isValid(self, s: str) -> bool:
        """
        Interview explanation:
        Every closing bracket must match the most recent unmatched opening
        bracket of the same type — classic stack nesting.

        Algorithm:
        - Map each closing bracket to its opening counterpart.
        - Scan left to right:
          - Opening bracket -> push onto the stack.
          - Closing bracket -> stack must be non-empty and top must match; pop.
        - Valid iff the stack is empty at the end.

        Complexity: O(n) time, O(n) space.
        """
        pairs = {')': '(', ']': '[', '}': '{'}
        stack = []

        for ch in s:
            if ch in pairs:
                if not stack or stack[-1] != pairs[ch]:
                    return False
                stack.pop()
            else:
                stack.append(ch)

        return not stack
# @lc code=end
