#
# @lc app=leetcode id=222 lang=python3
#
# [222] Count Complete Tree Nodes
#
# https://leetcode.com/problems/count-complete-tree-nodes/description/
#
# algorithms
# Medium (73.04%)
# Likes:    9594
# Dislikes: 626
# Total Accepted:    1.2M
# Total Submissions: 1.7M
# Testcase Example:  "[1,2,3,4,5,6]"
#
# Given the root of a complete binary tree, return the number of the nodes in
# the tree.
#
# According to Wikipedia, every level, except possibly the last, is completely
# filled in a complete binary tree, and all nodes in the last level are as far
# left as possible. It can have between 1 and 2^h nodes inclusive at the last
# level h.
#
# Design an algorithm that runs in less than O(n) time complexity.
#
# Example 1:
#
# Input: root = [1,2,3,4,5,6]
# Output: 6
#
# Example 2:
#
# Input: root = []
# Output: 0
#
# Example 3:
#
# Input: root = [1]
# Output: 1
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 5 * 10^4].
#
# 0 <= Node.val <= 5 * 10^4
#
# The tree is guaranteed to be complete.
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
    def countNodes(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        In a complete tree, left and right heights often match: the subtree is
        perfect with 2^h - 1 nodes. If heights differ, recurse into the side
        that is still complete, achieving better than O(n).

        Algorithm:
        - Compute left-spine height hl and right-spine height hr.
        - If hl == hr, return 2^hl - 1.
        - Else return 1 + count(left) + count(right).

        Complexity: O(log^2 n) time, O(log n) recursion space.
        """
        if not root:
            return 0

        def left_height(node: Optional[TreeNode]) -> int:
            h = 0
            while node:
                h += 1
                node = node.left
            return h

        def right_height(node: Optional[TreeNode]) -> int:
            h = 0
            while node:
                h += 1
                node = node.right
            return h

        hl = left_height(root)
        hr = right_height(root)
        if hl == hr:
            return (1 << hl) - 1
        return 1 + self.countNodes(root.left) + self.countNodes(root.right)
# @lc code=end
