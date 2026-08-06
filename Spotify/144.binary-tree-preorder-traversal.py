#
# @lc app=leetcode id=144 lang=python3
#
# [144] Binary Tree Preorder Traversal
#
# https://leetcode.com/problems/binary-tree-preorder-traversal/description/
#
# algorithms
# Easy (76.39%)
# Likes:    8981
# Dislikes: 237
# Total Accepted:    2.6M
# Total Submissions: 3.4M
# Testcase Example:  "[1,null,2,3]"
#
# Given the root of a binary tree, return the preorder traversal of its nodes'
# values.
#
# Example 1:
#
# Input: root = [1,null,2,3]
#
# Output: [1,2,3]
#
# Explanation:
#
# Example 2:
#
# Input: root = [1,2,3,4,5,null,8,null,null,6,7,9]
#
# Output: [1,2,4,5,6,7,3,8,9]
#
# Explanation:
#
# Example 3:
#
# Input: root = []
#
# Output: []
#
# Example 4:
#
# Input: root = [1]
#
# Output: [1]
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 100].
#
# -100 <= Node.val <= 100
#
# Follow up: Recursive solution is trivial, could you do it iteratively?
#

# @lc code=start
from typing import List, Optional
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def preorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        """
        Interview explanation:
        Preorder is Node -> Left -> Right. Recursion follows the definition
        directly.

        Algorithm:
        - Visit node, recurse left, recurse right.

        Complexity: O(n) time, O(h) recursion space.
        """
        ans: List[int] = []

        def dfs(node: Optional[TreeNode]) -> None:
            if not node:
                return
            ans.append(node.val)
            dfs(node.left)
            dfs(node.right)

        dfs(root)
        return ans

    def preorderTraversalIterative(self, root: Optional[TreeNode]) -> List[int]:
        """
        Interview explanation:
        Iterative preorder uses a stack. Push right before left so left is
        processed first (LIFO).

        Algorithm:
        - Start with root on the stack.
        - Pop, visit, push right then left if present.

        Complexity: O(n) time, O(h) stack space.
        """
        if not root:
            return []
        ans: List[int] = []
        stack: List[TreeNode] = [root]
        while stack:
            node = stack.pop()
            ans.append(node.val)
            if node.right:
                stack.append(node.right)
            if node.left:
                stack.append(node.left)
        return ans
# @lc code=end
