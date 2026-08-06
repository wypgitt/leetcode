#
# @lc app=leetcode id=224 lang=python3
#
# [224] Basic Calculator
#
# https://leetcode.com/problems/basic-calculator/description/
#
# algorithms
# Hard (47.08%)
# Likes:    7035
# Dislikes: 563
# Total Accepted:    733K
# Total Submissions: 1.6M
# Testcase Example:  "\"1 + 1\""
#
# Given a string s representing a valid expression, implement a basic
# calculator to evaluate it, and return the result of the evaluation.
#
# Note: You are not allowed to use any built-in function which evaluates
# strings as mathematical expressions, such as eval().
#
# Example 1:
#
# Input: s = "1 + 1"
# Output: 2
#
# Example 2:
#
# Input: s = " 2-1 + 2 "
# Output: 3
#
# Example 3:
#
# Input: s = "(1+(4+5+2)-3)+(6+8)"
# Output: 23
#
# Constraints:
#
# 1 <= s.length <= 3 * 10^5
#
# s consists of digits, '+', '-', '(', ')', and ' '.
#
# s represents a valid expression.
#
# '+' is not used as a unary operation (i.e., "+1" and "+(2 + 3)" is invalid).
#
# '-' could be used as a unary operation (i.e., "-1" and "-(2 + 3)" is valid).
#
# There will be no two consecutive operators in the input.
#
# Every number and running calculation will fit in a signed 32-bit integer.
#

# @lc code=start
class Solution:
    def calculate(self, s: str) -> int:
        """
        Interview explanation:
        Evaluate '+'/'-' and parentheses with a stack. On '(', push the running
        result and sign, then reset; on ')', pop and combine. Digits build the
        current number.

        Algorithm:
        - Track result, sign (+1/-1), and num.
        - Digits: accumulate num.
        - '+'/'-': apply previous num with sign; update sign.
        - '(': push result and sign; reset result/sign.
        - ')': apply num; result = popped_result + popped_sign * result.

        Complexity: O(n) time, O(n) space for nesting depth.
        """
        stack = []
        result = 0
        num = 0
        sign = 1
        for ch in s:
            if ch.isdigit():
                num = num * 10 + int(ch)
            elif ch in "+-":
                result += sign * num
                num = 0
                sign = 1 if ch == "+" else -1
            elif ch == "(":
                stack.append(result)
                stack.append(sign)
                result = 0
                sign = 1
            elif ch == ")":
                result += sign * num
                num = 0
                result *= stack.pop()  # sign before '('
                result += stack.pop()  # result before '('
        return result + sign * num
# @lc code=end
