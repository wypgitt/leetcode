from __future__ import annotations


class Solution:
    def reverseParentheses(self, s: str) -> str:
        stack = []

        for char in s:
            if char == ")":
                reversed_part = []
                while stack[-1] != "(":
                    reversed_part.append(stack.pop())
                stack.pop()
                stack.extend(reversed_part)
            else:
                stack.append(char)

        return "".join(stack)

