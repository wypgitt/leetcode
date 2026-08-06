#
# @lc app=leetcode id=3749 lang=python3
#
# [3749] Evaluate Valid Expressions
#
# https://leetcode.com/problems/evaluate-valid-expressions/description/
#
# algorithms
# Hard (69.75%)
# Likes:    4
# Dislikes: 1
# Total Accepted:    528
# Total Submissions: 757
# Testcase Example:  "\"add(2,3)\""
#
#
# You are given a string expression that represents a nested mathematical
# expression in a simplified form.
#
# A valid expression is either an integer literal or follows the format
# op(a,b), where:
#
# op is one of "add", "sub", "mul", or "div".
#
# a and b are each valid expressions.
#
# The operations are defined as follows:
#
# add(a,b) = a + b
#
# sub(a,b) = a - b
#
# mul(a,b) = a * b
#
# div(a,b) = a / b
#
# Return an integer representing the result after fully evaluating the
# expression.
#
# Example 1:
#
# Input: expression = "add(2,3)"
#
# Output: 5
#
# Explanation:
#
# The operation add(2,3) means 2 + 3 = 5.
#
# Example 2:
#
# Input: expression = "-42"
#
# Output: -42
#
# Explanation:
#
# The expression is a single integer literal, so the result is -42.
#
# Example 3:
#
# Input: expression = "div(mul(4,sub(9,5)),add(1,1))"
#
# Output: 8
#
# Explanation:
#
# First, evaluate the inner expression: sub(9,5) = 9 - 5 = 4
#
# Next, multiply the results: mul(4,4) = 4 * 4 = 16
#
# Then, compute the addition on the right: add(1,1) = 1 + 1 = 2
#
# Finally, divide the two main results: div(16,2) = 16 / 2 = 8
#
# Therefore, the entire expression evaluates to 8.
#
# Constraints:
#
# 1 <= expression.length <= 10^5
#
# expression is valid and consists of digits, commas, parentheses, the
# minus sign '-', and the lowercase strings "add", "sub", "mul", "div".
#
# All intermediate results fit within the range of a long integer.
#
# All divisions result in integer values.
#

# @lc code=start
class Solution:
    def evaluateExpression(self, expression: str) -> int:
        """
        Interview explanation:
        Parse nested op(a,b) with op in {add,sub,mul,div}, or a bare integer
        (possibly negative). Divisions are exact integers.

        Algorithm:
        - Recursive descent / index walk: if digit or '-', parse int; else read
          op name, '(', recurse for a, ',', recurse for b, ')'.

        Complexity: O(n) time, O(depth) space.
        """
        n = len(expression)
        i = 0

        def parse() -> int:
            nonlocal i
            if expression[i].isdigit() or expression[i] == "-":
                sign = 1
                if expression[i] == "-":
                    sign = -1
                    i += 1
                val = 0
                while i < n and expression[i].isdigit():
                    val = val * 10 + ord(expression[i]) - 48
                    i += 1
                return sign * val

            # op name
            j = i
            while expression[j] != "(":
                j += 1
            op = expression[i:j]
            i = j + 1  # skip '('
            a = parse()
            i += 1  # skip ','
            b = parse()
            i += 1  # skip ')'
            if op == "add":
                return a + b
            if op == "sub":
                return a - b
            if op == "mul":
                return a * b
            return a // b  # div, exact

        return parse()
# @lc code=end
