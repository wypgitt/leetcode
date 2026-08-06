#
# @lc app=leetcode id=2232 lang=python3
#
# [2232] Minimize Result by Adding Parentheses to Expression
#
# https://leetcode.com/problems/minimize-result-by-adding-parentheses-to-expression/description/
#
# algorithms
# Medium (68.31%)
# Likes:    227
# Dislikes: 345
# Total Accepted:    28.3K
# Total Submissions: 41.4K
# Testcase Example:  "\"247+38\""
#
# You are given a 0-indexed string expression of the form "<num1>+<num2>" where
# <num1> and <num2> represent positive integers.
#
# Add a pair of parentheses to expression such that after the addition of
# parentheses, expression is a valid mathematical expression and evaluates to
# the smallest possible value. The left parenthesis must be added to the left of
# '+' and the right parenthesis must be added to the right of '+'.
#
# Return expression after adding a pair of parentheses such that expression
# evaluates to the smallest possible value. If there are multiple answers that
# yield the same result, return any of them.
#
# The input has been generated such that the original value of expression, and
# the value of expression after adding any pair of parentheses that meets the
# requirements fits within a signed 32-bit integer.
#
#
#
# Example 1:
#
# Input: expression = "247+38"
# Output: "2(47+38)"
# Explanation: The expression evaluates to 2 * (47 + 38) = 2 * 85 = 170.
# Note that "2(4)7+38" is invalid because the right parenthesis must be to the
# right of the '+'.
# It can be shown that 170 is the smallest possible value.
#
# Example 2:
#
# Input: expression = "12+34"
# Output: "1(2+3)4"
# Explanation: The expression evaluates to 1 * (2 + 3) * 4 = 1 * 5 * 4 = 20.
#
# Example 3:
#
# Input: expression = "999+999"
# Output: "(999+999)"
# Explanation: The expression evaluates to 999 + 999 = 1998.
#
#
#
# Constraints:
#
#
# 3 <= expression.length <= 10
#
#
# expression consists of digits from '1' to '9' and '+'.
#
#
# expression starts and ends with digits.
#
#
# expression contains exactly one '+'.
#
#
# The original value of expression, and the value of expression after adding any
# pair of parentheses that meets the requirements fits within a signed 32-bit
# integer.
#

# @lc code=start
class Solution:
    def minimizeResult(self, expression: str) -> str:
        """
        Interview explanation:
        expression = num1+num2. Add parentheses to form a*(b+c)*d minimizing the
        value, where a|b = num1 split and c|d = num2 split (a,d may be empty=1).

        Algorithm:
        - Enumerate split points i in num1 and j in num2; evaluate; track best
          parenthesized string.

        Complexity: O(L^2) time, O(L) space.
        """
        plus = expression.index("+")
        left, right = expression[:plus], expression[plus + 1 :]
        best_val = float("inf")
        best_expr = ""
        for i in range(len(left)):
            for j in range(1, len(right) + 1):
                a = left[:i]
                b = left[i:]
                c = right[:j]
                d = right[j:]
                val = (int(a) if a else 1) * (int(b) + int(c)) * (int(d) if d else 1)
                expr = f"{a}({b}+{c}){d}"
                if val < best_val:
                    best_val = val
                    best_expr = expr
        return best_expr
# @lc code=end
