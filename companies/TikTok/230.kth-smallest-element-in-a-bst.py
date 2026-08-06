"""
Approach: Iterative inorder traversal until the kth visited node.
Data structure: a stack stores the path to the next smallest unvisited node.
Interview logic: inorder traversal of a BST visits values in sorted order. Decrement k each time a node is popped; the node that makes k zero is the answer.
Complexity: O(h + k) time, O(h) space for tree height h.
Tests and edge cases: k=1 returns the minimum; k=n returns the maximum; skewed trees use O(n) stack in worst case.
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
class Solution:
    def kthSmallest(self, root: Optional[TreeNode], k: int) -> int:
        stack = []
        node = root
        while True:
            while node:
                stack.append(node)
                node = node.left
            node = stack.pop()
            k -= 1
            if k == 0:
                return node.val
            node = node.right
# @lc code=end
