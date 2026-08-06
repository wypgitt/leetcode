#
# @lc app=leetcode id=701 lang=python3
#
# [701] Insert into a Binary Search Tree
#
# https://leetcode.com/problems/insert-into-a-binary-search-tree/description/
#
# algorithms
# Medium (73.6%)
# Likes:    6535
# Dislikes: 190
# Total Accepted:    930K
# Total Submissions: 1.3M
# Testcase Example:  "[4,2,7,1,3]"
#
# You are given the root node of a binary search tree (BST) and a value to
# insert into the tree. Return the root node of the BST after the insertion. It
# is guaranteed that the new value does not exist in the original BST.
#
# Notice that there may exist multiple valid ways for the insertion, as long as
# the tree remains a BST after insertion. You can return any of them.
#
# Example 1:
#
# Input: root = [4,2,7,1,3], val = 5
# Output: [4,2,7,1,3,5]
# Explanation: Another accepted tree is:
#
# Example 2:
#
# Input: root = [40,20,60,10,30,50,70], val = 25
# Output: [40,20,60,10,30,50,70,null,null,25]
#
# Example 3:
#
# Input: root = [4,2,7,1,3,null,null,null,null,null,null], val = 5
# Output: [4,2,7,1,3,5]
#
# Constraints:
#
# The number of nodes in the tree will be in the range [0, 10^4].
#
# -10^8 <= Node.val <= 10^8
#
# All the values Node.val are unique.
#
# -10^8 <= val <= 10^8
#
# It's guaranteed that val does not exist in the original BST.
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
    def insertIntoBST(self, root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
        """
        Interview explanation:
        Insert val as a new leaf preserving BST order. Walk left/right until a
        null child slot; attach TreeNode(val). Recursive or iterative both fine.

        Algorithm:
        - If root is None return new node. Else recurse/walk to insert side.

        Complexity: O(h) time, O(h) recursion / O(1) iterative space.
        """
        if not root:
            return TreeNode(val)
        if val < root.val:
            root.left = self.insertIntoBST(root.left, val)
        else:
            root.right = self.insertIntoBST(root.right, val)
        return root

    def insertIntoBSTIterative(self, root: Optional[TreeNode], val: int) -> Optional[TreeNode]:
        """
        Interview explanation:
        Iterative insert: walk to null child, attach new node; handle empty root.

        Algorithm:
        - If empty return TreeNode(val). Else parent walk until leaf edge.

        Complexity: O(h) time, O(1) space.
        """
        node = TreeNode(val)
        if not root:
            return node
        cur = root
        while True:
            if val < cur.val:
                if not cur.left:
                    cur.left = node
                    return root
                cur = cur.left
            else:
                if not cur.right:
                    cur.right = node
                    return root
                cur = cur.right
# @lc code=end
