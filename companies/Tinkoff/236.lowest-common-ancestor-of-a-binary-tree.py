"""
Approach: Postorder recursion returning whether p or q was found in each subtree.
Data structure: recursion explores both sides because a general binary tree has no ordering property.
Interview logic: if root is p or q, return root. Otherwise ask left and right subtrees. If both return non-null, root is the split point and the LCA; otherwise propagate the non-null side upward.
Complexity: O(n) time, O(h) recursion space.
Tests and edge cases: one target can be ancestor of the other; nodes may be on different sides; skewed trees have O(n) stack depth.
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
        if not root or root is p or root is q:
            return root
        left = self.lowestCommonAncestor(root.left, p, q)
        right = self.lowestCommonAncestor(root.right, p, q)
        if left and right:
            return root
        return left or right
# @lc code=end
