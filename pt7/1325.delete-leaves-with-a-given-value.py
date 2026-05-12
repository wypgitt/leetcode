#
# @lc app=leetcode id=1325 lang=python3
#
# [1325] Delete Leaves With a Given Value
#
# https://leetcode.com/problems/delete-leaves-with-a-given-value/description/
#
# algorithms
# Medium (77.25%)
# Likes:    2911
# Dislikes: 59
# Total Accepted:    257.9K
# Total Submissions: 333.8K
# Testcase Example:  '[1,2,3,2,null,2,4]\n2'
#
# Given a binary tree root and an integer target, delete all the leaf nodes
# with value target.
# 
# Note that once you delete a leaf node with value target, if its parent node
# becomes a leaf node and has the value target, it should also be deleted (you
# need to continue doing that until you cannot).
# 
# 
# Example 1:
# 
# 
# 
# 
# Input: root = [1,2,3,2,null,2,4], target = 2
# Output: [1,null,3,null,4]
# Explanation: Leaf nodes in green with value (target = 2) are removed (Picture
# in left). 
# After removing, new nodes become leaf nodes with value (target = 2) (Picture
# in center).
# 
# 
# Example 2:
# 
# 
# 
# 
# Input: root = [1,3,3,3,2], target = 3
# Output: [1,3,null,null,2]
# 
# 
# Example 3:
# 
# 
# 
# 
# Input: root = [1,2,null,2,null,2], target = 2
# Output: [1]
# Explanation: Leaf nodes in green with value (target = 2) are removed at each
# step.
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [1, 3000].
# 1 <= Node.val, target <= 1000
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import Optional


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def removeLeafNodes(self, root: Optional[TreeNode], target: int) -> Optional[TreeNode]:
        if root is None:
            return None

        root.left = self.removeLeafNodes(root.left, target)
        root.right = self.removeLeafNodes(root.right, target)

        if root.left is None and root.right is None and root.val == target:
            return None

        return root
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Deleting a leaf can make its parent become a new leaf that also needs to be
# deleted. That means we must process children before deciding whether the
# current node should remain: a postorder DFS.
#
# Data structure:
# Recursion mirrors the tree. Each call returns the possibly updated subtree
# root, which lets the parent reconnect to a pruned child or `None`.
#
# Walkthrough:
# 1. Recursively prune the left subtree.
# 2. Recursively prune the right subtree.
# 3. After both children are finalized, check whether the current node is now a
#    target-valued leaf.
# 4. Return `None` if it should be deleted; otherwise return the node.
#
# Edge cases:
# - Root itself may be deleted, so the function returns the new root.
# - Cascading deletions are handled by postorder traversal.
# - Empty subtree returns `None`.
#
# Complexity:
# - Time: O(n), each node is visited once.
# - Space: O(h), recursion stack height.
