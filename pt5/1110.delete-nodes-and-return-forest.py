from __future__ import annotations

from typing import List, Optional


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def delNodes(self, root: Optional[TreeNode], to_delete: List[int]) -> List[TreeNode]:
        deleted_values = set(to_delete)
        forest = []

        def prune(node: Optional[TreeNode], is_root: bool) -> Optional[TreeNode]:
            if node is None:
                return None

            deleted = node.val in deleted_values
            if is_root and not deleted:
                forest.append(node)

            node.left = prune(node.left, deleted)
            node.right = prune(node.right, deleted)
            return None if deleted else node

        prune(root, True)
        return forest

