#
# @lc app=leetcode id=439 lang=python3
#
# [439] Ternary Expression Parser
#
# https://leetcode.com/problems/ternary-expression-parser/description/
#
# algorithms
# Medium (62.58%)
# Likes:    514
# Dislikes: 74
# Total Accepted:    38.8K
# Total Submissions: 61.9K
# Testcase Example:  '"T?2:3"'
#
# Given a string expression representing arbitrarily nested ternary
# expressions, evaluate the expression, and return the result of it.
# 
# You can always assume that the given expression is valid and only contains
# digits, '?', ':', 'T', and 'F' where 'T' is true and 'F' is false. All the
# numbers in the expression are one-digit numbers (i.e., in the range [0, 9]).
# 
# The conditional expressions group right-to-left (as usual in most languages),
# and the result of the expression will always evaluate to either a digit, 'T'
# or 'F'.
# 
# 
# Example 1:
# 
# 
# Input: expression = "T?2:3"
# Output: "2"
# Explanation: If true, then result is 2; otherwise result is 3.
# 
# 
# Example 2:
# 
# 
# Input: expression = "F?1:T?4:5"
# Output: "4"
# Explanation: The conditional expressions group right-to-left. Using
# parenthesis, it is read/evaluated as:
# "(F ? 1 : (T ? 4 : 5))" --> "(F ? 1 : 4)" --> "4"
# or "(F ? 1 : (T ? 4 : 5))" --> "(T ? 4 : 5)" --> "4"
# 
# 
# Example 3:
# 
# 
# Input: expression = "T?T?F:5:3"
# Output: "F"
# Explanation: The conditional expressions group right-to-left. Using
# parenthesis, it is read/evaluated as:
# "(T ? (T ? F : 5) : 3)" --> "(T ? F : 3)" --> "F"
# "(T ? (T ? F : 5) : 3)" --> "(T ? F : 5)" --> "F"
# 
# 
# 
# Constraints:
# 
# 
# 5 <= expression.length <= 10^4
# expression consists of digits, 'T', 'F', '?', and ':'.
# It is guaranteed that expression is a valid ternary expression and that each
# number is a one-digit number.
# 
# 
#

# @lc code=start
class Solution:
    def parseTernary(self, expression: str) -> str:
        stack = []
        for ch in reversed(expression):
            if stack and stack[-1] == '?':
                stack.pop()
                true_expr = stack.pop()
                stack.pop()  # ':'
                false_expr = stack.pop()
                stack.append(true_expr if ch == 'T' else false_expr)
            elif ch != ':':
                stack.append(ch)
            else:
                stack.append(ch)
        return stack[-1]
# @lc code=end

"""
Interview explanation:
Ternary expressions are right-associative, so parsing from right to left makes each condition see already-resolved true and false branches. When the top of the stack is '?', the current character is the condition; pop '?', true branch, ':', false branch, and push the selected branch.

Data structure: the stack stores unresolved tokens and resolved subexpressions.

Edge cases: nested ternaries work because the innermost/rightmost expression is collapsed first. Leaf values are single characters per the problem constraints.

Complexity: each character is pushed and popped at most once, so time is O(n) and space is O(n).
"""
