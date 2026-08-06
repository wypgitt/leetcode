#
# @lc app=leetcode id=450 lang=python3
#
# [450] Delete Node in a BST
#
# https://leetcode.com/problems/delete-node-in-a-bst/description/
#
# algorithms
# Medium (55.21%)
# Likes:    10594
# Dislikes: 396
# Total Accepted:    924K
# Total Submissions: 1.7M
# Testcase Example:  "[5,3,6,2,4,null,7]"
#
# Given a root node reference of a BST and a key, delete the node with the
# given key in the BST. Return the root node reference (possibly updated) of
# the BST.
#
# Basically, the deletion can be divided into two stages:
#
# Search for a node to remove.
#
# If the node is found, delete the node.
#
# Example 1:
#
# Input: root = [5,3,6,2,4,null,7], key = 3
# Output: [5,4,6,2,null,null,7]
# Explanation: Given key to delete is 3. So we find the node with value 3 and
# delete it.
# One valid answer is [5,4,6,2,null,null,7], shown in the above BST.
# Please notice that another valid answer is [5,2,6,null,4,null,7] and it's
# also accepted.
#
# Example 2:
#
# Input: root = [5,3,6,2,4,null,7], key = 0
# Output: [5,3,6,2,4,null,7]
# Explanation: The tree does not contain a node with value = 0.
#
# Example 3:
#
# Input: root = [], key = 0
# Output: []
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 10^4].
#
# -10^5 <= Node.val <= 10^5
#
# Each node has a unique value.
#
# root is a valid binary search tree.
#
# -10^5 <= key <= 10^5
#
# Follow up: Could you solve it with time complexity O(height of tree)?
#

# @lc code=start
from typing import Optional

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

try:
    TreeNode  # type: ignore[name-defined]
except NameError:
    class TreeNode:
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def deleteNode(self, root: Optional[TreeNode], key: int) -> Optional[TreeNode]:
        """
        Interview explanation:
        Standard BST delete: search for key, then handle 0/1/2 children.
        With two children, replace with inorder successor (min of right),
        then delete that successor from the right subtree.

        Algorithm:
        - If key < root.val: delete in left; elif key > root.val: in right.
        - Else: no left -> return right; no right -> return left;
          else find min(right), copy val, delete that min from right.

        Complexity: O(h) time, O(h) recursion space (h = height).
        """
        if not root:
            return None
        if key < root.val:
            root.left = self.deleteNode(root.left, key)
        elif key > root.val:
            root.right = self.deleteNode(root.right, key)
        else:
            if not root.left:
                return root.right
            if not root.right:
                return root.left
            succ = root.right
            while succ.left:
                succ = succ.left
            root.val = succ.val
            root.right = self.deleteNode(root.right, succ.val)
        return root
# @lc code=end
