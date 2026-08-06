"""
Approach: DFS while carrying the numeric value represented by the current root-to-node path.
Data structure: recursion is the path stack; no string/list of digits is needed.
Interview logic: appending a digit is current * 10 + node.val. A leaf completes one number, so summing leaf values counts every root-to-leaf number exactly once.
Complexity: O(n) time for n nodes, O(h) stack space for tree height h.
Tests and edge cases: empty tree returns 0; a single node returns its digit; zeros are handled by the arithmetic formula.
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
    def sumNumbers(self, root: Optional[TreeNode]) -> int:
        def dfs(node: Optional[TreeNode], current: int) -> int:
            if not node:
                return 0
            current = current * 10 + node.val
            if not node.left and not node.right:
                return current
            return dfs(node.left, current) + dfs(node.right, current)
        return dfs(root, 0)
# @lc code=end
