#
# @lc app=leetcode id=1021 lang=python3
#
# [1021] Remove Outermost Parentheses
#
# https://leetcode.com/problems/remove-outermost-parentheses/description/
#
# algorithms
# Easy (87.36%)
# Likes:    3845
# Dislikes: 1736
# Total Accepted:    726K
# Total Submissions: 831K
# Testcase Example:  "\"(()())(())\""
#
# A valid parentheses string is either empty "", "(" + A + ")", or A + B, where
# A and B are valid parentheses strings, and + represents string concatenation.
#
# For example, "", "()", "(())()", and "(()(()))" are all valid parentheses
# strings.
#
# A valid parentheses string s is primitive if it is nonempty, and there does
# not exist a way to split it into s = A + B, with A and B nonempty valid
# parentheses strings.
#
# Given a valid parentheses string s, consider its primitive decomposition: s =
# P_1 + P_2 + ... + P_k, where P_i are primitive valid parentheses strings.
#
# Return s after removing the outermost parentheses of every primitive string
# in the primitive decomposition of s.
#
# Example 1:
#
# Input: s = "(()())(())"
# Output: "()()()"
# Explanation:
# The input string is "(()())(())", with primitive decomposition "(()())" +
# "(())".
# After removing outer parentheses of each part, this is "()()" + "()" =
# "()()()".
#
# Example 2:
#
# Input: s = "(()())(())(()(()))"
# Output: "()()()()(())"
# Explanation:
# The input string is "(()())(())(()(()))", with primitive decomposition
# "(()())" + "(())" + "(()(()))".
# After removing outer parentheses of each part, this is "()()" + "()" +
# "()(())" = "()()()()(())".
#
# Example 3:
#
# Input: s = "()()"
# Output: ""
# Explanation:
# The input string is "()()", with primitive decomposition "()" + "()".
# After removing outer parentheses of each part, this is "" + "" = "".
#
# Constraints:
#
# 1 <= s.length <= 10^5
#
# s[i] is either '(' or ')'.
#
# s is a valid parentheses string.
#

# @lc code=start
class Solution:
    def removeOuterParentheses(self, s: str) -> str:
        """
        Interview explanation:
        Primitive decomposition: track depth. Characters with depth>0 after
        processing '(' or before processing ')' are inner; skip outermost.

        Algorithm:
        - depth=0; for c in s: if '(': depth++; if depth>1: append; else: if depth>1: append; depth--

        Complexity: O(n) time, O(n) space for output.
        """
        ans = []
        depth = 0
        for c in s:
            if c == "(":
                if depth > 0:
                    ans.append(c)
                depth += 1
            else:
                depth -= 1
                if depth > 0:
                    ans.append(c)
        return "".join(ans)

    def removeOuterParentheses_stack(self, s: str) -> str:
        """
        Interview explanation:
        Alternate: stack of indices of open parens; when stack empties after a
        close, that span was a primitive — strip its outer parens.

        Algorithm:
        - Scan with stack; on empty stack after ')', take s[start+1:i]

        Complexity: O(n) time, O(n) space.
        """
        ans = []
        stack = []
        start = 0
        for i, c in enumerate(s):
            if c == "(":
                stack.append(i)
            else:
                stack.pop()
                if not stack:
                    ans.append(s[start + 1 : i])
                    start = i + 1
        return "".join(ans)
# @lc code=end
