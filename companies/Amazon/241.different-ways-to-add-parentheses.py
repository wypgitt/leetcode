"""
Approach: Divide and conquer with memoization on expression substrings.
Data structure: lru_cache stores results for each substring to avoid recomputing overlapping subexpressions.
Interview logic: every operator can be the last operation performed. Compute all possible left values and right values around that operator and combine them.
Complexity: exponential output size; memoization avoids repeated parsing of the same substring. Space is proportional to cached subexpressions and output lists.
Tests and edge cases: pure number returns that number; multiple operators with same precedence are all parenthesized; negative intermediate values are valid.
"""
from __future__ import annotations
from functools import lru_cache
from typing import List

# @lc code=start
from functools import lru_cache
class Solution:
    def diffWaysToCompute(self, expression: str) -> List[int]:
        @lru_cache(None)
        def solve(expr: str) -> tuple[int, ...]:
            results = []
            for i, ch in enumerate(expr):
                if ch in '+-*':
                    for a in solve(expr[:i]):
                        for b in solve(expr[i + 1:]):
                            if ch == '+':
                                results.append(a + b)
                            elif ch == '-':
                                results.append(a - b)
                            else:
                                results.append(a * b)
            if not results:
                results.append(int(expr))
            return tuple(results)
        return list(solve(expression))
# @lc code=end
