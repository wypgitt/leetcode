"""
Approach: Walk down the BST using value ordering.
Data structure: a single pointer is enough because BST ordering tells which subtree can contain both targets.
Interview logic: if both p and q are smaller than root, LCA is in the left subtree. If both are larger, it is in the right subtree. Otherwise root splits the paths and is the LCA.
Complexity: O(h) time, O(1) space.
Tests and edge cases: one node can be ancestor of the other; p and q on different sides return root; skewed tree height can be n.
"""
from __future__ import annotations

# @lc code=start
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None
class Solution:
    def lowestCommonAncestor(self, root: 'TreeNode', p: 'TreeNode', q: 'TreeNode') -> 'TreeNode':
        low, high = sorted((p.val, q.val))
        node = root
        while node:
            if high < node.val:
                node = node.left
            elif low > node.val:
                node = node.right
            else:
                return node
# @lc code=end
