#
# @lc app=leetcode id=1382 lang=python3
#
# [1382] Balance a Binary Search Tree
#
# https://leetcode.com/problems/balance-a-binary-search-tree/description/
#
# algorithms
# Medium (86.28%)
# Likes:    4180
# Dislikes: 105
# Total Accepted:    405.4K
# Total Submissions: 469.9K
# Testcase Example:  '[1,null,2,null,3,null,4]'
#
# Given the root of a binary search tree, return a balanced binary search tree
# with the same node values. If there is more than one answer, return any of
# them.
# 
# A binary search tree is balanced if the depth of the two subtrees of every
# node never differs by more than 1.
# 
# 
# Example 1:
# 
# 
# Input: root = [1,null,2,null,3,null,4,null,null]
# Output: [2,1,3,null,null,null,4]
# Explanation: This is not the only correct answer, [3,1,4,null,2] is also
# correct.
# 
# 
# Example 2:
# 
# 
# Input: root = [2,1,3]
# Output: [2,1,3]
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [1, 10^4].
# 1 <= Node.val <= 10^5
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import List, Optional


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def balanceBST(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        values: List[int] = []

        def inorder(node: Optional[TreeNode]) -> None:
            if node is None:
                return
            inorder(node.left)
            values.append(node.val)
            inorder(node.right)

        def build(left: int, right: int) -> Optional[TreeNode]:
            if left > right:
                return None

            mid = (left + right) // 2
            node = TreeNode(values[mid])
            node.left = build(left, mid - 1)
            node.right = build(mid + 1, right)
            return node

        inorder(root)
        return build(0, len(values) - 1)
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Inorder traversal of a BST gives sorted values. A height-balanced BST can be
# built from a sorted array by choosing the middle value as root recursively.
#
# Data structures:
# A list stores sorted node values. Recursion builds the balanced tree from
# index ranges.
#
# Walkthrough:
# 1. Traverse the original BST inorder into `values`.
# 2. Pick the middle element as the new root.
# 3. Recursively build the left subtree from the left half and the right subtree
#    from the right half.
# 4. Return the rebuilt root.
#
# Edge cases:
# - Empty tree: inorder list is empty and build returns None.
# - Already balanced tree: result may have a different shape but remains valid
#   and balanced.
# - Duplicate values: inorder order preserves BST sorted order.
#
# Complexity:
# - Time: O(n), one traversal and one rebuild pass.
# - Space: O(n), for values and the new tree recursion stack.
#
# Improvement:
# We could reuse original TreeNode objects instead of allocating new ones. New
# nodes make the explanation straightforward and avoid pointer cleanup issues.
