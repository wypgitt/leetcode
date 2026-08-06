#
# @lc app=leetcode id=897 lang=python3
#
# [897] Increasing Order Search Tree
#
# https://leetcode.com/problems/increasing-order-search-tree/description/
#
# algorithms
# Easy (79.07%)
# Likes:    4505
# Dislikes: 686
# Total Accepted:    347K
# Total Submissions: 438K
# Testcase Example:  "[5,3,6,2,4,null,8,1,null,null,null,7,9]"
#
# Given the root of a binary search tree, rearrange the tree in in-order so
# that the leftmost node in the tree is now the root of the tree, and every
# node has no left child and only one right child.
#
# Example 1:
#
# Input: root = [5,3,6,2,4,null,8,1,null,null,null,7,9]
# Output: [1,null,2,null,3,null,4,null,5,null,6,null,7,null,8,null,9]
#
# Example 2:
#
# Input: root = [5,1,7]
# Output: [1,null,5,null,7]
#
# Constraints:
#
# The number of nodes in the given tree will be in the range [1, 100].
#
# 0 <= Node.val <= 1000
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
    def increasingBST(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        """
        Interview explanation:
        Rearrange BST into right-only increasing chain via inorder traversal;
        link nodes as we visit (or collect then rebuild).

        Algorithm (inorder relink):
        - Dummy sentinel; cur=dummy. Inorder: node.left=None; cur.right=node;
          cur=node. Return dummy.right.

        Complexity: O(n) time, O(h) recursion space.
        """
        dummy = TreeNode(0)
        self.cur = dummy

        def inorder(node: Optional[TreeNode]) -> None:
            if not node:
                return
            inorder(node.left)
            node.left = None
            self.cur.right = node
            self.cur = node
            inorder(node.right)

        inorder(root)
        return dummy.right

    def increasingBST_collect(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        """
        Interview explanation:
        Alternate: collect inorder values/nodes into a list, then wire right chain.

        Algorithm:
        - vals via inorder; build TreeNode chain from vals.

        Complexity: O(n) time/space.
        """
        vals: List[int] = []

        def inorder(node: Optional[TreeNode]) -> None:
            if not node:
                return
            inorder(node.left)
            vals.append(node.val)
            inorder(node.right)

        inorder(root)
        dummy = TreeNode(0)
        cur = dummy
        for v in vals:
            cur.right = TreeNode(v)
            cur = cur.right
        return dummy.right
# @lc code=end

