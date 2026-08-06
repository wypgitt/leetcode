#
# @lc app=leetcode id=226 lang=python3
#
# [226] Invert Binary Tree
#
# https://leetcode.com/problems/invert-binary-tree/description/
#
# algorithms
# Easy (80.33%)
# Likes:    15338
# Dislikes: 255
# Total Accepted:    3.2M
# Total Submissions: 3.9M
# Testcase Example:  "[4,2,7,1,3,6,9]"
#
# Given the root of a binary tree, invert the tree, and return its root.
#
# Example 1:
#
# Input: root = [4,2,7,1,3,6,9]
# Output: [4,7,2,9,6,3,1]
#
# Example 2:
#
# Input: root = [2,1,3]
# Output: [2,3,1]
#
# Example 3:
#
# Input: root = []
# Output: []
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 100].
#
# -100 <= Node.val <= 100
#

# @lc code=start
from collections import deque
from typing import Optional
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def invertTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        """
        Interview explanation:
        Invert means swap left/right at every node. Recursive DFS: invert
        subtrees then swap children (or swap then recurse — same result).

        Algorithm:
        - If root is None, return None.
        - Recurse on left and right; assign swapped children; return root.

        Complexity: O(n) time, O(h) recursion space.
        """
        if not root:
            return None
        root.left, root.right = self.invertTree(root.right), self.invertTree(root.left)
        return root

    def invertTreeBFS(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        """
        Interview explanation:
        Level-order BFS: for each node, swap children and enqueue them.
        Same O(n) work, iterative queue instead of recursion.

        Algorithm:
        - Queue root; while queue: pop, swap left/right, enqueue non-null children.

        Complexity: O(n) time, O(w) space for max width w.
        """
        if not root:
            return None
        q = deque([root])
        while q:
            node = q.popleft()
            node.left, node.right = node.right, node.left
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        return root
# @lc code=end
