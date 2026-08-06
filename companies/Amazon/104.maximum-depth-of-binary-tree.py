#
# @lc app=leetcode id=104 lang=python3
#
# [104] Maximum Depth of Binary Tree
#
# https://leetcode.com/problems/maximum-depth-of-binary-tree/description/
#
# algorithms
# Easy (78.48%)
# Likes:    14469
# Dislikes: 297
# Total Accepted:    5.0M
# Total Submissions: 6.4M
# Testcase Example:  "[3,9,20,null,null,15,7]"
#
# Given the root of a binary tree, return its maximum depth.
#
# A binary tree's maximum depth is the number of nodes along the longest path
# from the root node down to the farthest leaf node.
#
# Example 1:
#
# Input: root = [3,9,20,null,null,15,7]
# Output: 3
#
# Example 2:
#
# Input: root = [1,null,2]
# Output: 2
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 10^4].
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
    def maxDepth(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Maximum depth is 1 plus the deeper of the two child subtrees. DFS
        returns that value bottom-up.

        Algorithm:
        - Empty node has depth 0.
        - Otherwise depth = 1 + max(left depth, right depth).

        Complexity: O(n) time, O(h) recursion space.
        """
        if not root:
            return 0
        return 1 + max(self.maxDepth(root.left), self.maxDepth(root.right))

    def maxDepthBFS(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Level-order BFS counts how many levels exist; the last level number is
        the maximum depth.

        Algorithm:
        - Process the tree level by level with a queue.
        - Increment depth once per level until the queue is empty.

        Complexity: O(n) time, O(w) queue space.
        """
        if not root:
            return 0
        depth = 0
        queue = deque([root])
        while queue:
            for _ in range(len(queue)):
                node = queue.popleft()
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            depth += 1
        return depth
# @lc code=end
