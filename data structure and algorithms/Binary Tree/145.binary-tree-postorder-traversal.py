#
# @lc app=leetcode id=145 lang=python3
#
# [145] Binary Tree Postorder Traversal
#
# https://leetcode.com/problems/binary-tree-postorder-traversal/description/
#
# algorithms
# Easy (78.75%)
# Likes:    7868
# Dislikes: 228
# Total Accepted:    2.1M
# Total Submissions: 2.6M
# Testcase Example:  "[1,null,2,3]"
#
# Given the root of a binary tree, return the postorder traversal of its nodes'
# values.
#
# Example 1:
#
# Input: root = [1,null,2,3]
#
# Output: [3,2,1]
#
# Explanation:
#
# Example 2:
#
# Input: root = [1,2,3,4,5,null,8,null,null,6,7,9]
#
# Output: [4,6,7,5,2,9,8,3,1]
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
# The number of the nodes in the tree is in the range [0, 100].
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
    def postorderTraversal(self, root: Optional[TreeNode]) -> List[int]:
        """
        Interview explanation:
        Postorder is Left -> Right -> Node. Recursion is the clearest form.

        Algorithm:
        - Recurse left, recurse right, then visit.

        Complexity: O(n) time, O(h) recursion space.
        """
        ans: List[int] = []

        def dfs(node: Optional[TreeNode]) -> None:
            if not node:
                return
            dfs(node.left)
            dfs(node.right)
            ans.append(node.val)

        dfs(root)
        return ans

    def postorderTraversalIterative(self, root: Optional[TreeNode]) -> List[int]:
        """
        Interview explanation:
        Classic iterative trick: do a modified preorder Node -> Right -> Left,
        then reverse the result to get Left -> Right -> Node.

        Algorithm:
        - Stack traversal visiting node then pushing left then right.
        - Reverse the collected list at the end.

        Complexity: O(n) time, O(h) stack space.
        """
        if not root:
            return []
        ans: List[int] = []
        stack: List[TreeNode] = [root]
        while stack:
            node = stack.pop()
            ans.append(node.val)
            if node.left:
                stack.append(node.left)
            if node.right:
                stack.append(node.right)
        ans.reverse()
        return ans
# @lc code=end
