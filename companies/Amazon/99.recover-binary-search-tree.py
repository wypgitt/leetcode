#
# @lc app=leetcode id=99 lang=python3
#
# [99] Recover Binary Search Tree
#
# https://leetcode.com/problems/recover-binary-search-tree/description/
#
# algorithms
# Medium (59.54%)
# Likes:    8626
# Dislikes: 292
# Total Accepted:    668.8K
# Total Submissions: 1.1M
# Testcase Example:  '[1,3,null,null,2]'
#
# You are given the root of a binary search tree (BST), where the values of
# exactly two nodes of the tree were swapped by mistake. Recover the tree
# without changing its structure.
# 
# 
# Example 1:
# 
# 
# Input: root = [1,3,null,null,2]
# Output: [3,1,null,null,2]
# Explanation: 3 cannot be a left child of 1 because 3 > 1. Swapping 1 and 3
# makes the BST valid.
# 
# 
# Example 2:
# 
# 
# Input: root = [3,1,4,null,null,2]
# Output: [2,1,4,null,null,3]
# Explanation: 2 cannot be in the right subtree of 3 because 2 < 3. Swapping 2
# and 3 makes the BST valid.
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [2, 1000].
# -2^31 <= Node.val <= 2^31 - 1
# 
# 
# 
# Follow up: A solution using O(n) space is pretty straight-forward. Could you
# devise a constant O(1) space solution?
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
    def recoverTree(self, root: Optional[TreeNode]) -> None:
        """
        Do not return anything, modify root in-place instead.

        Interview explanation:
        An inorder traversal of a BST should be strictly increasing. Swapping two
        nodes creates one or two inversions in that sequence. The first misplaced
        node is the previous node in the first inversion; the second misplaced
        node is the current node in the last inversion. Swapping their values
        restores the BST without changing structure.

        Edge cases and tests:
        - Adjacent swapped nodes create one inversion.
        - Non-adjacent swapped nodes create two inversions.
        - Tree shape is unchanged; only values are swapped.

        Complexity: O(n) time, O(h) recursion space. Morris traversal could make
        auxiliary space O(1), but recursive inorder is simpler and interview-safe.
        """
        first = second = prev = None

        def inorder(node: Optional[TreeNode]) -> None:
            nonlocal first, second, prev
            if not node:
                return
            inorder(node.left)
            if prev and prev.val > node.val:
                if not first:
                    first = prev
                second = node
            prev = node
            inorder(node.right)

        inorder(root)
        first.val, second.val = second.val, first.val
# @lc code=end


