#
# @lc app=leetcode id=700 lang=python3
#
# [700] Search in a Binary Search Tree
#
# https://leetcode.com/problems/search-in-a-binary-search-tree/description/
#
# algorithms
# Easy (83.03%)
# Likes:    6661
# Dislikes: 221
# Total Accepted:    1.5M
# Total Submissions: 1.8M
# Testcase Example:  "[4,2,7,1,3]"
#
# You are given the root of a binary search tree (BST) and an integer val.
#
# Find the node in the BST that the node's value equals val and return the
# subtree rooted with that node. If such a node does not exist, return null.
#
# Example 1:
#
# Input: root = [4,2,7,1,3], val = 2
# Output: [2,1,3]
#
# Example 2:
#
# Input: root = [4,2,7,1,3], val = 5
# Output: []
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 5000].
#
# 1 <= Node.val <= 10^7
#
# root is a binary search tree.
#
# 1 <= val <= 10^7
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
    def searchBST(self, root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
        """
        Interview explanation:
        BST search: go left if val < node.val, right if greater, return node on
        match. Iterative form is preferred to avoid recursion depth.

        Algorithm:
        - While root: if equal return; elif val < root.val go left else right.

        Complexity: O(h) time, O(1) space.
        """
        while root and root.val != val:
            root = root.left if val < root.val else root.right
        return root

    def searchBSTRecursive(self, root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
        """
        Interview explanation:
        Recursive BST search — elegant mirror of the iterative approach.

        Algorithm:
        - Base None or match; recurse left/right by comparison.

        Complexity: O(h) time, O(h) space.
        """
        if not root or root.val == val:
            return root
        if val < root.val:
            return self.searchBSTRecursive(root.left, val)
        return self.searchBSTRecursive(root.right, val)
# @lc code=end
