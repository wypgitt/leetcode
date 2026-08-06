#
# @lc app=leetcode id=1896 lang=python3
#
# [1896] Minimum Cost to Change the Final Value of Expression
#
# https://leetcode.com/problems/minimum-cost-to-change-the-final-value-of-expression/description/
#
# algorithms
# Hard (49.83%)
# Likes:    249
# Dislikes: 43
# Total Accepted:    5.6K
# Total Submissions: 11.2K
# Testcase Example:  "\"1&(0|1)\""
#
# You are given a valid boolean expression as a string expression consisting of
# the characters '1','0','&' (bitwise AND operator),'|' (bitwise OR
# operator),'(', and ')'.
#
# For example, "()1|1" and "(1)&()" are not valid while "1", "(((1))|(0))", and
# "1|(0&(1))" are valid expressions.
#
# Return the minimum cost to change the final value of the expression.
#
# For example, if expression = "1|1|(0&0)&1", its value is 1|1|(0&0)&1 =
# 1|1|0&1 = 1|0&1 = 1&1 = 1. We want to apply operations so that the new
# expression evaluates to 0.
#
# The cost of changing the final value of an expression is the number of
# operations performed on the expression. The types of operations are described
# as follows:
#
# Turn a '1' into a '0'.
#
# Turn a '0' into a '1'.
#
# Turn a '&' into a '|'.
#
# Turn a '|' into a '&'.
#
# Note: '&' does not take precedence over '|' in the order of calculation.
# Evaluate parentheses first, then in left-to-right order.
#
# Example 1:
#
# Input: expression = "1&(0|1)"
# Output: 1
# Explanation: We can turn "1&(0|1)" into "1&(0&1)" by changing the '|' to a
# '&' using 1 operation.
# The new expression evaluates to 0.
#
# Example 2:
#
# Input: expression = "(0&0)&(0&0&0)"
# Output: 3
# Explanation: We can turn "(0&0)&(0&0&0)" into "(0|1)|(0&0&0)" using 3
# operations.
# The new expression evaluates to 1.
#
# Example 3:
#
# Input: expression = "(0|(1|0&1))"
# Output: 1
# Explanation: We can turn "(0|(1|0&1))" into "(0|(0|0&1))" using 1 operation.
# The new expression evaluates to 0.
#
# Constraints:
#
# 1 <= expression.length <= 10^5
#
# expression only contains '1','0','&','|','(', and ')'
#
# All parentheses are properly matched.
#
# There will be no empty parentheses (i.e: "()" is not a substring of
# expression).
#

# @lc code=start
class Solution:
    def minOperationsToFlip(self, expression: str) -> int:
        """
        Interview explanation:
        Min ops to flip the expression's value. Ops: flip a bit 0↔1, or flip an
        operator &↔|. Parse left-associative expression with a stack storing
        (value_char, min_cost_to_flip).

        Algorithm (stack):
        - Push '(', '&', '|' as markers.
        - On '0'/'1' or after ')': if top is an operator, pop op and left; combine
          with right into new (val, flip_cost) using case analysis:
          & 00 → 1+min; & 01/10 → 1; & 11 → min; | symmetric.
        - Answer = flip cost of final value.

        Complexity: O(n) time/space.
        """
        stack = []  # (expr_char_or_marker, cost)

        for e in expression:
            if e in "(&|":
                stack.append((e, 0))
                continue
            if e == ")":
                last = stack.pop()
                stack.pop()  # '('
            else:
                last = (e, 1)
            if stack and stack[-1][0] in "&|":
                op = stack.pop()[0]
                a, costA = stack.pop()
                b, costB = last
                if op == "&":
                    if a == "0" and b == "0":
                        last = ("0", 1 + min(costA, costB))
                    elif a == "1" and b == "1":
                        last = ("1", min(costA, costB))
                    else:
                        last = ("0", 1)
                else:  # '|'
                    if a == "0" and b == "0":
                        last = ("0", min(costA, costB))
                    elif a == "1" and b == "1":
                        last = ("1", 1 + min(costA, costB))
                    else:
                        last = ("1", 1)
            stack.append(last)

        return stack[-1][1]
# @lc code=end
