#
# @lc app=leetcode id=282 lang=python3
#
# [282] Expression Add Operators
#
# https://leetcode.com/problems/expression-add-operators/description/
#
# algorithms
# Hard (43.6%)
# Likes:    3820
# Dislikes: 735
# Total Accepted:    329K
# Total Submissions: 756K
# Testcase Example:  "\"123\""
#
# Given a string num that contains only digits and an integer target, return
# all possibilities to insert the binary operators '+', '-', and/or '*' between
# the digits of num so that the resultant expression evaluates to the target
# value.
#
# Note that operands in the returned expressions should not contain leading
# zeros.
#
# Note that a number can contain multiple digits.
#
# Example 1:
#
# Input: num = "123", target = 6
# Output: ["1*2*3","1+2+3"]
# Explanation: Both "1*2*3" and "1+2+3" evaluate to 6.
#
# Example 2:
#
# Input: num = "232", target = 8
# Output: ["2*3+2","2+3*2"]
# Explanation: Both "2*3+2" and "2+3*2" evaluate to 8.
#
# Example 3:
#
# Input: num = "3456237490", target = 9191
# Output: []
# Explanation: There are no expressions that can be created from "3456237490"
# to evaluate to 9191.
#
# Constraints:
#
# 1 <= num.length <= 10
#
# num consists of only digits.
#
# -2^31 <= target <= 2^31 - 1
#

# @lc code=start
from typing import List


class Solution:
    def addOperators(self, num: str, target: int) -> List[str]:
        """
        Interview explanation:
        Insert '+', '-', or '*' between digits (or concatenate) so expression
        equals target. Backtrack over split points; track running value and the
        last multiplied operand to undo multiplication associativity.

        Algorithm:
        - At index i, take every non-empty substring num[i:j] as the next operand
          (skip leading zeros unless the operand is "0").
        - For '+'/'-'/'*'/concat: update value and last accordingly.
        - When i == n and value == target, record the expression.

        Complexity: O(4^n) expressions explored, O(n) recursion depth.
        """
        n = len(num)
        ans: List[str] = []

        def dfs(i: int, expr: str, value: int, last: int) -> None:
            if i == n:
                if value == target:
                    ans.append(expr)
                return
            for j in range(i + 1, n + 1):
                s = num[i:j]
                if len(s) > 1 and s[0] == "0":
                    break
                cur = int(s)
                if i == 0:
                    dfs(j, s, cur, cur)
                else:
                    dfs(j, expr + "+" + s, value + cur, cur)
                    dfs(j, expr + "-" + s, value - cur, -cur)
                    dfs(j, expr + "*" + s, value - last + last * cur, last * cur)

        dfs(0, "", 0, 0)
        return ans
# @lc code=end

