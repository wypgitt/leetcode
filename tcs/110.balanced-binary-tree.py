#
# @lc app=leetcode id=110 lang=python3
#
# [110] Balanced Binary Tree
#
# https://leetcode.com/problems/balanced-binary-tree/description/
#
# algorithms
# Easy (58.93%)
# Likes:    12348
# Dislikes: 848
# Total Accepted:    2.6M
# Total Submissions: 4.4M
# Testcase Example:  "[3,9,20,null,null,15,7]"
#
# Given a binary tree, determine if it is height-balanced.
#
# Example 1:
#
# Input: root = [3,9,20,null,null,15,7]
# Output: true
#
# Example 2:
#
# Input: root = [1,2,2,3,3,null,null,4,4]
# Output: false
#
# Example 3:
#
# Input: root = []
# Output: true
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 5000].
#
# -10^4 <= Node.val <= 10^4
#

# @lc code=start
from typing import Optional
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def isBalanced(self, root: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        Height-balanced means every node has |left_height - right_height| <= 1.
        The optimal check is bottom-up: compute height while validating balance
        in one DFS pass (avoid the O(n^2) top-down recompute).

        Algorithm:
        - DFS returns height, or -1 if the subtree is unbalanced.
        - At each node, if either child is -1 or heights differ by > 1, return -1.
        - Otherwise return 1 + max(left, right).
        - Tree is balanced iff the root DFS is not -1.

        Complexity: O(n) time, O(h) recursion space.
        """
        def height(node: Optional[TreeNode]) -> int:
            if not node:
                return 0
            left = height(node.left)
            if left == -1:
                return -1
            right = height(node.right)
            if right == -1 or abs(left - right) > 1:
                return -1
            return 1 + max(left, right)

        return height(root) != -1
# @lc code=end
