#
# @lc app=leetcode id=105 lang=python3
#
# [105] Construct Binary Tree from Preorder and Inorder Traversal
#
# https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/description/
#
# algorithms
# Medium (68.77%)
# Likes:    16694
# Dislikes: 637
# Total Accepted:    1.9M
# Total Submissions: 2.7M
# Testcase Example:  '[3,9,20,15,7]\n[9,3,15,20,7]'
#
# Given two integer arrays preorder and inorder where preorder is the preorder
# traversal of a binary tree and inorder is the inorder traversal of the same
# tree, construct and return the binary tree.
# 
# 
# Example 1:
# 
# 
# Input: preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]
# Output: [3,9,20,null,null,15,7]
# 
# 
# Example 2:
# 
# 
# Input: preorder = [-1], inorder = [-1]
# Output: [-1]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= preorder.length <= 3000
# inorder.length == preorder.length
# -3000 <= preorder[i], inorder[i] <= 3000
# preorder and inorder consist of unique values.
# Each value of inorder also appears in preorder.
# preorder is guaranteed to be the preorder traversal of the tree.
# inorder is guaranteed to be the inorder traversal of the tree.
# 
# 
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
    def buildTree(self, preorder: List[int], inorder: List[int]) -> Optional[TreeNode]:
        """
        Interview explanation:
        Preorder gives the root first. Inorder tells how many nodes belong to
        the left and right subtrees around that root. A value-to-index map avoids
        O(n) searches for every node.

        Algorithm:
        - preorder[pre_l] is the root of the current subtree.
        - Find its inorder index mid.
        - left_size = mid - in_l.
        - Recursively build left and right ranges.

        Edge cases and tests:
        - Empty range returns None.
        - Single node builds a leaf.
        - Skewed trees are handled by empty left or right ranges.

        Complexity: O(n) time, O(n) space for map plus recursion stack.
        """
        index = {value: i for i, value in enumerate(inorder)}

        def build(pre_l: int, pre_r: int, in_l: int, in_r: int) -> Optional[TreeNode]:
            if pre_l > pre_r:
                return None
            root_val = preorder[pre_l]
            mid = index[root_val]
            left_size = mid - in_l
            root = TreeNode(root_val)
            root.left = build(pre_l + 1, pre_l + left_size, in_l, mid - 1)
            root.right = build(pre_l + left_size + 1, pre_r, mid + 1, in_r)
            return root

        return build(0, len(preorder) - 1, 0, len(inorder) - 1)
# @lc code=end


