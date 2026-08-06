#
# @lc app=leetcode id=678 lang=python3
#
# [678] Valid Parenthesis String
#
# https://leetcode.com/problems/valid-parenthesis-string/description/
#
# algorithms
# Medium (40.37%)
# Likes:    7111
# Dislikes: 227
# Total Accepted:    629K
# Total Submissions: 1.6M
# Testcase Example:  "\"()\""
#
# Given a string s containing only three types of characters: '(', ')' and '*',
# return true if s is valid.
#
# The following rules define a valid string:
#
# Any left parenthesis '(' must have a corresponding right parenthesis ')'.
#
# Any right parenthesis ')' must have a corresponding left parenthesis '('.
#
# Left parenthesis '(' must go before the corresponding right parenthesis ')'.
#
# '*' could be treated as a single right parenthesis ')' or a single left
# parenthesis '(' or an empty string "".
#
# Example 1:
#
# Input: s = "()"
# Output: true
#
# Example 2:
#
# Input: s = "(*)"
# Output: true
#
# Example 3:
#
# Input: s = "(*))"
# Output: true
#
# Constraints:
#
# 1 <= s.length <= 100
#
# s[i] is '(', ')' or '*'.
#

# @lc code=start
class Solution:
    def checkValidString(self, s: str) -> bool:
        """
        Interview explanation:
        '*' can be '(', ')' or empty. Greedy two-pass / balance range: track the
        possible open-count interval [lo, hi]. '(' increases both; ')' decreases
        both; '*' decreases lo (as ')') and increases hi (as '(').

        Algorithm:
        - lo, hi = 0, 0. For each char update lo/hi; if hi < 0 fail; lo = max(lo,0).
        - Valid iff lo == 0 at end.

        Complexity: O(n) time, O(1) space.
        """
        lo = hi = 0
        for c in s:
            if c == "(":
                lo += 1
                hi += 1
            elif c == ")":
                lo -= 1
                hi -= 1
            else:
                lo -= 1
                hi += 1
            if hi < 0:
                return False
            lo = max(lo, 0)
        return lo == 0

    def checkValidStringStack(self, s: str) -> bool:
        """
        Interview explanation:
        Classic stack approach: store indices of '(' and '*'. Match ')' with
        latest '(' else '*'. Remaining '(' must be matched by later '*' to their right.

        Algorithm:
        - left and star stacks; then while left: need star index > left index.

        Complexity: O(n) time and space.
        """
        left, star = [], []
        for i, c in enumerate(s):
            if c == "(":
                left.append(i)
            elif c == "*":
                star.append(i)
            else:
                if left:
                    left.pop()
                elif star:
                    star.pop()
                else:
                    return False
        while left and star:
            if left[-1] > star[-1]:
                return False
            left.pop()
            star.pop()
        return not left
# @lc code=end
