"""
Approach: Simulate BST preorder with a monotonic stack and a lower bound.
Data structure: the stack holds ancestors whose right subtree has not been entered yet.
Interview logic: preorder visits root, then left subtree, then right subtree. When a value is greater than stack top, we are moving up into a right subtree, so popped ancestors become the new lower bound. Any later value below that bound violates the BST rule.
Complexity: O(n) time, O(n) space.
Tests and edge cases: empty or one-element sequence is valid; descending sequence is valid as all-left children; a value below the lower bound is invalid.
"""
from __future__ import annotations
from typing import List

# @lc code=start
class Solution:
    def verifyPreorder(self, preorder: List[int]) -> bool:
        stack = []
        lower = float('-inf')
        for value in preorder:
            if value < lower:
                return False
            while stack and value > stack[-1]:
                lower = stack.pop()
            stack.append(value)
        return True
# @lc code=end
