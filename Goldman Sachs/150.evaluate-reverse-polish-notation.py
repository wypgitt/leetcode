"""
Approach: Stack evaluation of postfix tokens.
Data structure: the stack stores operands until an operator consumes the top two values.
Interview logic: in RPN, every operator appears after its left and right operands. Pop right first, then left, apply the operation, and push the reduced value.
Complexity: O(n) time, O(n) space.
Tests and edge cases: division truncates toward zero, so Python floor division cannot be used directly for negatives; one number alone returns itself.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def evalRPN(self, tokens: List[str]) -> int:
        stack: List[int] = []
        for token in tokens:
            if token not in '+-*/':
                stack.append(int(token))
                continue
            b, a = stack.pop(), stack.pop()
            if token == '+':
                stack.append(a + b)
            elif token == '-':
                stack.append(a - b)
            elif token == '*':
                stack.append(a * b)
            else:
                sign = -1 if (a < 0) ^ (b < 0) else 1
                stack.append(sign * (abs(a) // abs(b)))
        return stack[-1]
# @lc code=end
