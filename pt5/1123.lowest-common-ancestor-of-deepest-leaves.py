from __future__ import annotations

from typing import Optional, Tuple


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def lcaDeepestLeaves(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        def dfs(node: Optional[TreeNode]) -> Tuple[int, Optional[TreeNode]]:
            if node is None:
                return 0, None

            left_depth, left_lca = dfs(node.left)
            right_depth, right_lca = dfs(node.right)

            if left_depth == right_depth:
                return left_depth + 1, node
            if left_depth > right_depth:
                return left_depth + 1, left_lca
            return right_depth + 1, right_lca

        return dfs(root)[1]

