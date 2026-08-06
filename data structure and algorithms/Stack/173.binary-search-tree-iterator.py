"""
Approach: Controlled iterative inorder traversal.
Data structure: a stack stores the path of left ancestors that are waiting to be visited.
Interview logic: the next smallest BST value is always at the top after pushing all left children. After popping it, push the left spine of its right subtree.
Complexity: next and hasNext are O(1) amortized; O(h) space for tree height h.
Tests and edge cases: empty tree makes hasNext false; skewed trees use O(n) stack in worst case; duplicate values preserve inorder order.
"""
from __future__ import annotations
from typing import Optional

# @lc code=start
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class BSTIterator:
    def __init__(self, root: Optional[TreeNode]):
        self.stack = []
        self._push_left(root)

    def _push_left(self, node: Optional[TreeNode]) -> None:
        while node:
            self.stack.append(node)
            node = node.left

    def next(self) -> int:
        node = self.stack.pop()
        self._push_left(node.right)
        return node.val

    def hasNext(self) -> bool:
        return bool(self.stack)
# @lc code=end
