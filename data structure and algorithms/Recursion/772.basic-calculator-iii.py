#
# @lc app=leetcode id=772 lang=python3
#
# [772] Basic Calculator III
#
# https://leetcode.com/problems/basic-calculator-iii/description/
#
# algorithms
# Hard (53.48%)
# Likes:    1182
# Dislikes: 295
# Total Accepted:    158.5K
# Total Submissions: 296.4K
# Testcase Example:  "\"1+1\""
#
#
# Implement a basic calculator to evaluate a simple expression string.
#
# The expression string contains only non-negative integers, '+', '-',
# '*', '/' operators, and open '(' and closing parentheses ')'. The
# integer division should truncate toward zero.
#
# You may assume that the given expression is always valid. All
# intermediate results will be in the range of [-2^31, 2^31 - 1].
#
# Note: You are not allowed to use any built-in function which evaluates
# strings as mathematical expressions, such as eval().
#
# Example 1:
#
# Input: s = "1+1"
# Output: 2
#
# Example 2:
#
# Input: s = "6-4/2"
# Output: 4
#
# Example 3:
#
# Input: s = "2*(5+5*2)/3+(6/2+8)"
# Output: 21
#
# Constraints:
#
# 1 <= s <= 10^4
#
# s consists of digits, '+', '-', '*', '/', '(', and ')'.
#
# s is a valid expression.
#
# @lc code=start
class Solution:
    def calculate(self, s: str) -> int:
        """
        Interview explanation:
        Premium. Evaluate +, -, *, /, parentheses, integers. Recursive descent
        respects precedence (* / over + -); parentheses recurse as sub-expr.
        Division truncates toward zero.

        Algorithm (recursive descent):
        - expr := term ((+|-) term)*
        - term := factor ((*|/) factor)*
        - factor := number | '(' expr ')' | unary (+|-) factor
        - int(a/b) for truncate-toward-zero division.

        Complexity: O(n) time, O(n) space (nesting depth).
        """
        s = s.replace(" ", "")
        n = len(s)
        i = 0

        def parse_expr() -> int:
            nonlocal i
            val = parse_term()
            while i < n and s[i] in "+-":
                op = s[i]
                i += 1
                rhs = parse_term()
                val = val + rhs if op == "+" else val - rhs
            return val

        def parse_term() -> int:
            nonlocal i
            val = parse_factor()
            while i < n and s[i] in "*/":
                op = s[i]
                i += 1
                rhs = parse_factor()
                if op == "*":
                    val *= rhs
                else:
                    val = int(val / rhs)
            return val

        def parse_factor() -> int:
            nonlocal i
            if i < n and s[i] == "(":
                i += 1
                val = parse_expr()
                i += 1  # ')'
                return val
            sign = 1
            if i < n and s[i] == "-":
                sign = -1
                i += 1
            elif i < n and s[i] == "+":
                i += 1
            num = 0
            while i < n and s[i].isdigit():
                num = num * 10 + ord(s[i]) - 48
                i += 1
            return sign * num

        return parse_expr()

    def calculate_stack(self, s: str) -> int:
        """
        Interview explanation:
        Alternate classic: one stack of (acc, pending_sign/op state) for
        parentheses; within a level, keep last_num and apply * / immediately,
        defer + - into acc until the next + - or end/close-paren.

        Algorithm:
        - Helper eval level from index; on '(': recurse; on ')': return.
        - Maintain acc, last (sign-applied term), op, num.
        - On + -: acc += last; last = ±num. On * /: last = last*/num.

        Complexity: O(n) time, O(n) space.
        """
        s = s.replace(" ", "")

        def helper(i: int):
            acc = 0
            last = 0
            num = 0
            op = "+"
            while i < len(s):
                ch = s[i]
                if ch.isdigit():
                    num = num * 10 + ord(ch) - 48
                    i += 1
                    continue
                if ch == "(":
                    num, i = helper(i + 1)
                    continue
                # operator, ')', or end-of-level trigger after consuming num
                if op == "+":
                    acc += last
                    last = num
                elif op == "-":
                    acc += last
                    last = -num
                elif op == "*":
                    last = last * num
                else:
                    last = int(last / num)
                num = 0
                if ch == ")":
                    return acc + last, i + 1
                op = ch
                i += 1
            if op == "+":
                acc += last
                last = num
            elif op == "-":
                acc += last
                last = -num
            elif op == "*":
                last = last * num
            else:
                last = int(last / num)
            return acc + last, i

        return helper(0)[0]
# @lc code=end


