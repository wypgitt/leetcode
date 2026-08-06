#
# @lc app=leetcode id=530 lang=python3
#
# [530] Minimum Absolute Difference in BST
#
# https://leetcode.com/problems/minimum-absolute-difference-in-bst/description/
#
# algorithms
# Easy (59.61%)
# Likes:    4790
# Dislikes: 277
# Total Accepted:    641K
# Total Submissions: 1.1M
# Testcase Example:  "[4,2,6,1,3]"
#
# Given the root of a Binary Search Tree (BST), return the minimum absolute
# difference between the values of any two different nodes in the tree.
#
# Example 1:
#
# Input: root = [4,2,6,1,3]
# Output: 1
#
# Example 2:
#
# Input: root = [1,0,48,null,null,12,49]
# Output: 1
#
# Constraints:
#
# The number of nodes in the tree is in the range [2, 10^4].
#
# 0 <= Node.val <= 10^5
#
# Note: This question is the same as 783:
# https://leetcode.com/problems/minimum-distance-between-bst-nodes/
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
    def getMinimumDifference(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Inorder traversal of a BST yields sorted values; the minimum absolute
        difference must be between two consecutive values in that order.

        Algorithm:
        - Inorder DFS; track previous value; update ans with val - prev.

        Complexity: O(n) time, O(h) recursion space.
        """
        self.prev = None
        self.ans = float("inf")

        def inorder(node: Optional[TreeNode]) -> None:
            if not node:
                return
            inorder(node.left)
            if self.prev is not None:
                self.ans = min(self.ans, node.val - self.prev)
            self.prev = node.val
            inorder(node.right)

        inorder(root)
        return self.ans
# @lc code=end

