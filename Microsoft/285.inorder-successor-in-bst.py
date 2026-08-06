#
# @lc app=leetcode id=285 lang=python3
#
# [285] Inorder Successor in BST
#
# https://leetcode.com/problems/inorder-successor-in-bst/description/
#
# algorithms
# Medium (51.26%)
# Likes:    2653
# Dislikes: 94
# Total Accepted:    374.1K
# Total Submissions: 729.9K
# Testcase Example:  "[2,1,3]\n1"
#
#
# Given the root of a binary search tree and a node p in it, return the
# in-order successor of that node in the BST. If the given node has no
# in-order successor in the tree, return null.
#
# The successor of a node p is the node with the smallest key greater than
# p.val.
#
# Example 1:
#
# Input: root = [2,1,3], p = 1
# Output: 2
# Explanation: 1's in-order successor node is 2. Note that both p and the
# return value is of TreeNode type.
#
# Example 2:
#
# Input: root = [5,3,6,2,4,null,null,1], p = 6
# Output: null
# Explanation: There is no in-order successor of the current node, so the
# answer is null.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# -10^5 <= Node.val <= 10^5
#
# All Nodes will have unique values.
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
    def inorderSuccessor(self, root: Optional[TreeNode], p: Optional[TreeNode]) -> Optional[TreeNode]:
        """
        Interview explanation:
        Inorder successor of p is the next larger node. If p has a right child,
        it is the leftmost node in that subtree; otherwise walk from root keeping
        the last ancestor greater than p.

        Algorithm (BST walk):
        - If p.right: go right once, then left until None.
        - Else: from root, if node.val > p.val record successor and go left;
          else go right.

        Complexity: O(h) time, O(1) space.
        """
        if p.right:
            node = p.right
            while node.left:
                node = node.left
            return node

        succ = None
        node = root
        while node:
            if node.val > p.val:
                succ = node
                node = node.left
            else:
                node = node.right
        return succ
# @lc code=end

