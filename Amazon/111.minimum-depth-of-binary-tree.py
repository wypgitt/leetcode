#
# @lc app=leetcode id=111 lang=python3
#
# [111] Minimum Depth of Binary Tree
#
# https://leetcode.com/problems/minimum-depth-of-binary-tree/description/
#
# algorithms
# Easy (53.5%)
# Likes:    7919
# Dislikes: 1370
# Total Accepted:    1.7M
# Total Submissions: 3.3M
# Testcase Example:  "[3,9,20,null,null,15,7]"
#
# Given a binary tree, find its minimum depth.
#
# The minimum depth is the number of nodes along the shortest path from the
# root node down to the nearest leaf node.
#
# Note: A leaf is a node with no children.
#
# Example 1:
#
# Input: root = [3,9,20,null,null,15,7]
# Output: 2
#
# Example 2:
#
# Input: root = [2,null,3,null,4,null,5,null,6]
# Output: 5
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 10^5].
#
# -1000 <= Node.val <= 1000
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
    def minDepth(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Minimum depth is the shortest root-to-leaf path. BFS finds the first
        leaf and can stop early, which is best when the shallowest leaf is near
        the top (skewed deep trees with a shallow sibling).

        Algorithm:
        - Level-order BFS; the first node with no children yields the depth.
        - Empty tree has depth 0.

        Complexity: O(n) time worst case, O(w) queue space; often early exit.
        """
        if not root:
            return 0
        queue = deque([(root, 1)])
        while queue:
            node, depth = queue.popleft()
            if not node.left and not node.right:
                return depth
            if node.left:
                queue.append((node.left, depth + 1))
            if node.right:
                queue.append((node.right, depth + 1))
        return 0

    def minDepthDFS(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        DFS computes min depth recursively. Careful with one-child nodes: a
        missing child is not a leaf, so take the non-empty child's depth.

        Algorithm:
        - Empty -> 0; leaf -> 1.
        - If one child is missing, recurse only into the existing child.
        - Otherwise 1 + min(left, right).

        Complexity: O(n) time, O(h) recursion space.
        """
        if not root:
            return 0
        if not root.left and not root.right:
            return 1
        if not root.left:
            return 1 + self.minDepthDFS(root.right)
        if not root.right:
            return 1 + self.minDepthDFS(root.left)
        return 1 + min(self.minDepthDFS(root.left), self.minDepthDFS(root.right))
# @lc code=end
