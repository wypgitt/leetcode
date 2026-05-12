#
# @lc app=leetcode id=1315 lang=python3
#
# [1315] Sum of Nodes with Even-Valued Grandparent
#
# https://leetcode.com/problems/sum-of-nodes-with-even-valued-grandparent/description/
#
# algorithms
# Medium (85.92%)
# Likes:    2832
# Dislikes: 79
# Total Accepted:    185.2K
# Total Submissions: 215.5K
# Testcase Example:  '[6,7,8,2,7,1,3,9,null,1,4,null,null,null,5]'
#
# Given the root of a binary tree, return the sum of values of nodes with an
# even-valued grandparent. If there are no nodes with an even-valued
# grandparent, return 0.
# 
# A grandparent of a node is the parent of its parent if it exists.
# 
# 
# Example 1:
# 
# 
# Input: root = [6,7,8,2,7,1,3,9,null,1,4,null,null,null,5]
# Output: 18
# Explanation: The red nodes are the nodes with even-value grandparent while
# the blue nodes are the even-value grandparents.
# 
# 
# Example 2:
# 
# 
# Input: root = [1]
# Output: 0
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [1, 10^4].
# 1 <= Node.val <= 100
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
    def sumEvenGrandparent(self, root: Optional[TreeNode]) -> int:
        def dfs(node: Optional[TreeNode], parent: Optional[TreeNode], grandparent: Optional[TreeNode]) -> int:
            if node is None:
                return 0

            total = node.val if grandparent and grandparent.val % 2 == 0 else 0
            total += dfs(node.left, node, parent)
            total += dfs(node.right, node, parent)
            return total

        return dfs(root, None, None)
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# During DFS, each node only needs to know its parent and grandparent. If the
# grandparent exists and has an even value, the current node contributes to the
# answer.
#
# Data structure:
# Recursion is enough because the tree structure already gives us the traversal
# order. We carry two ancestor references instead of storing paths.
#
# Walkthrough:
# 1. Visit a node with `(parent, grandparent)` context.
# 2. Add `node.val` only when `grandparent.val` is even.
# 3. Recurse to children, shifting the context: current node becomes parent,
#    old parent becomes grandparent.
#
# Edge cases:
# - Root and children of root have no grandparent, so they cannot be counted.
# - Negative values are not present in the constraints, but parity logic would
#   still work.
# - Empty tree returns 0 defensively.
#
# Complexity:
# - Time: O(n), every node is visited once.
# - Space: O(h), recursion stack height.
