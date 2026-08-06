"""
Approach: Postorder DFS that returns whether each subtree is univalue.
Data structure: recursion naturally computes child results before the parent; a counter accumulates valid subtrees.
Interview logic: a subtree is univalue if both child subtrees are univalue and every existing child root has the same value as the current root. Count it exactly when that condition holds.
Complexity: O(n) time, O(h) stack space.
Tests and edge cases: empty tree returns 0; leaves are univalue; mixed child values prevent the parent from counting.
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
    def countUnivalSubtrees(self, root: Optional[TreeNode]) -> int:
        count = 0
        def dfs(node: Optional[TreeNode]) -> bool:
            nonlocal count
            if not node:
                return True
            left_ok = dfs(node.left)
            right_ok = dfs(node.right)
            if not left_ok or not right_ok:
                return False
            if node.left and node.left.val != node.val:
                return False
            if node.right and node.right.val != node.val:
                return False
            count += 1
            return True
        dfs(root)
        return count
# @lc code=end
