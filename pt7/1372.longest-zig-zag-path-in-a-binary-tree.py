#
# @lc app=leetcode id=1372 lang=python3
#
# [1372] Longest ZigZag Path in a Binary Tree
#
# https://leetcode.com/problems/longest-zigzag-path-in-a-binary-tree/description/
#
# algorithms
# Medium (67.09%)
# Likes:    3759
# Dislikes: 86
# Total Accepted:    286.8K
# Total Submissions: 427.3K
# Testcase Example:  '[1,null,1,1,1,null,null,1,1,null,1,null,null,null,1]'
#
# You are given the root of a binary tree.
# 
# A ZigZag path for a binary tree is defined as follow:
# 
# 
# Choose any node in the binary tree and a direction (right or left).
# If the current direction is right, move to the right child of the current
# node; otherwise, move to the left child.
# Change the direction from right to left or from left to right.
# Repeat the second and third steps until you can't move in the tree.
# 
# 
# Zigzag length is defined as the number of nodes visited - 1. (A single node
# has a length of 0).
# 
# Return the longest ZigZag path contained in that tree.
# 
# 
# Example 1:
# 
# 
# Input: root = [1,null,1,1,1,null,null,1,1,null,1,null,null,null,1]
# Output: 3
# Explanation: Longest ZigZag path in blue nodes (right -> left -> right).
# 
# 
# Example 2:
# 
# 
# Input: root = [1,1,1,null,1,null,null,1,1,null,1]
# Output: 4
# Explanation: Longest ZigZag path in blue nodes (left -> right -> left ->
# right).
# 
# 
# Example 3:
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
# The number of nodes in the tree is in the range [1, 5 * 10^4].
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
    def longestZigZag(self, root: Optional[TreeNode]) -> int:
        best = 0

        def dfs(node: Optional[TreeNode]) -> tuple[int, int]:
            nonlocal best
            if node is None:
                return -1, -1

            left_left, left_right = dfs(node.left)
            right_left, right_right = dfs(node.right)

            go_left = left_right + 1
            go_right = right_left + 1
            best = max(best, go_left, go_right)
            return go_left, go_right

        dfs(root)
        return best
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# For each node, keep two values:
# - longest ZigZag starting at this node if the first move goes left.
# - longest ZigZag starting at this node if the first move goes right.
# After moving left, the next move must go right, and vice versa.
#
# Data structure:
# Postorder recursion returns a pair `(go_left, go_right)` for each subtree.
#
# Why return -1 for None:
# A leaf should have `go_left = 0` and `go_right = 0`, meaning no edge can be
# taken. Since leaf children return -1, adding 1 gives 0.
#
# Walkthrough:
# 1. Recursively compute the pair for both children.
# 2. `go_left = child's go_right + 1`.
# 3. `go_right = child's go_left + 1`.
# 4. Track the maximum path length seen anywhere.
#
# Edge cases:
# - Single node: answer 0 because path length counts edges.
# - Straight chain: longest ZigZag may be 1 if directions cannot alternate.
# - Empty root defensively returns 0 through initial `best`.
#
# Complexity:
# - Time: O(n), one visit per node.
# - Space: O(h), recursion stack height.
