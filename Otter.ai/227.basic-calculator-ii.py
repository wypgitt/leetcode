"""
Approach: Single pass with a stack of signed terms.
Data structure: the stack stores additive terms after immediately resolving multiplication and division precedence.
Interview logic: when an operator is reached, apply the previous operator to the completed number. Addition/subtraction push signed numbers; multiplication/division update the previous stack term.
Complexity: O(n) time, O(n) space.
Tests and edge cases: spaces are ignored; integer division truncates toward zero; the final number is processed by appending a sentinel operator.
"""
from __future__ import annotations

# @lc code=start
class Solution:
    def calculate(self, s: str) -> int:
        stack = []
        num = 0
        op = '+'
        for ch in s + '+':
            if ch == ' ':
                continue
            if ch.isdigit():
                num = num * 10 + int(ch)
                continue
            if op == '+':
                stack.append(num)
            elif op == '-':
                stack.append(-num)
            elif op == '*':
                stack[-1] *= num
            else:
                prev = stack.pop()
                sign = -1 if prev < 0 else 1
                stack.append(sign * (abs(prev) // num))
            op = ch
            num = 0
        return sum(stack)
# @lc code=end
