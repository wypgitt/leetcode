#
# @lc app=leetcode id=106 lang=python3
#
# [106] Construct Binary Tree from Inorder and Postorder Traversal
#
# https://leetcode.com/problems/construct-binary-tree-from-inorder-and-postorder-traversal/description/
#
# algorithms
# Medium (68.56%)
# Likes:    8713
# Dislikes: 159
# Total Accepted:    956.1K
# Total Submissions: 1.4M
# Testcase Example:  '[9,3,15,20,7]\n[9,15,7,20,3]'
#
# Given two integer arrays inorder and postorder where inorder is the inorder
# traversal of a binary tree and postorder is the postorder traversal of the
# same tree, construct and return the binary tree.
# 
# 
# Example 1:
# 
# 
# Input: inorder = [9,3,15,20,7], postorder = [9,15,7,20,3]
# Output: [3,9,20,null,null,15,7]
# 
# 
# Example 2:
# 
# 
# Input: inorder = [-1], postorder = [-1]
# Output: [-1]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= inorder.length <= 3000
# postorder.length == inorder.length
# -3000 <= inorder[i], postorder[i] <= 3000
# inorder and postorder consist of unique values.
# Each value of postorder also appears in inorder.
# inorder is guaranteed to be the inorder traversal of the tree.
# postorder is guaranteed to be the postorder traversal of the tree.
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
    def buildTree(self, inorder: List[int], postorder: List[int]) -> Optional[TreeNode]:
        """
        Interview explanation:
        Postorder gives the root last. Inorder splits the values into left and
        right subtrees. A value-to-index map lets each split be O(1), so every
        node is built once.

        Algorithm:
        - postorder[post_r] is the root.
        - Find root in inorder; left_size gives range sizes.
        - Build left from the first left_size postorder values and right from the
          following values.

        Edge cases and tests:
        - Empty subtree range returns None.
        - Single node returns a leaf.
        - Fully skewed trees work with one empty side.

        Complexity: O(n) time, O(n) space.
        """
        index = {value: i for i, value in enumerate(inorder)}

        def build(in_l: int, in_r: int, post_l: int, post_r: int) -> Optional[TreeNode]:
            if in_l > in_r:
                return None
            root_val = postorder[post_r]
            mid = index[root_val]
            left_size = mid - in_l
            root = TreeNode(root_val)
            root.left = build(in_l, mid - 1, post_l, post_l + left_size - 1)
            root.right = build(mid + 1, in_r, post_l + left_size, post_r - 1)
            return root

        return build(0, len(inorder) - 1, 0, len(postorder) - 1)
# @lc code=end


