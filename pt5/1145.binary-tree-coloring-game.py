from __future__ import annotations

from typing import Optional


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def btreeGameWinningMove(self, root: Optional[TreeNode], n: int, x: int) -> bool:
        left_size = right_size = 0

        def subtree_size(node: Optional[TreeNode]) -> int:
            nonlocal left_size, right_size
            if node is None:
                return 0

            left = subtree_size(node.left)
            right = subtree_size(node.right)
            if node.val == x:
                left_size = left
                right_size = right
            return left + right + 1

        subtree_size(root)
        parent_side = n - left_size - right_size - 1
        return max(left_size, right_size, parent_side) > n // 2

