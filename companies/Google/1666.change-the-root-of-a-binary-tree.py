#
# @lc app=leetcode id=1666 lang=python3
#
# [1666] Change the Root of a Binary Tree
#
# https://leetcode.com/problems/change-the-root-of-a-binary-tree/description/
#
# algorithms
# Medium (75.03%)
# Likes:    69
# Dislikes: 201
# Total Accepted:    6.1K
# Total Submissions: 8.1K
# Testcase Example:  "[3,5,1,6,2,0,8,null,null,7,4]\n7"
#
#
# Given the root of a binary tree and a leaf node, reroot the tree so that
# the leaf is the new root.
#
# You can reroot the tree with the following steps for each node cur on
# the path starting from the leaf up to the root​​​ excluding the root:
#
# If cur has a left child, then that child becomes cur's right child.
#
# cur's original parent becomes cur's left child. Note that in this
# process the original parent's pointer to cur becomes null, making it
# have at most one child.
#
# Return the new root of the rerooted tree.
#
# Note: Ensure that your solution sets the Node.parent pointers correctly
# after rerooting or you will receive "Wrong Answer".
#
# Example 1:
#
# Input: root = [3,5,1,6,2,0,8,null,null,7,4], leaf = 7
# Output: [7,2,null,5,4,3,6,null,null,null,1,null,null,0,8]
#
# Example 2:
#
# Input: root = [3,5,1,6,2,0,8,null,null,7,4], leaf = 0
# Output: [0,1,null,3,8,5,null,null,null,6,2,null,null,7,4]
#
# Constraints:
#
# The number of nodes in the tree is in the range [2, 100].
#
# -10^9 <= Node.val <= 10^9
#
# All Node.val are unique.
#
# leaf exist in the tree.
#
# @lc code=start
from typing import Optional


# Definition for a Node.
class Node:
    def __init__(self, val=0, left=None, right=None, parent=None):
        self.val = val
        self.left = left
        self.right = right
        self.parent = parent


class Solution:
    def flipBinaryTree(self, root: "Node", leaf: "Node") -> "Node":
        """
        Interview explanation:
        Premium. Reroot tree at leaf: walk from leaf to original root, flipping
        parent→child edges so each node on the path becomes child of the previous
        (new parent). Maintain left/right: if node had left, move left to right
        before attaching old parent as left (problem's specified rules).

        Algorithm:
        - cur=leaf; while cur != root: parent=cur.parent; detach cur from parent;
          if cur.left: cur.right=cur.left; set cur.left=parent; parent.parent=cur;
          advance. Clear new root's parent.

        Complexity: O(h) time, O(1) space.
        """
        cur = leaf
        while True:
            parent = cur.parent
            if parent is None:
                break
            # detach cur from parent
            if parent.left is cur:
                parent.left = None
            else:
                parent.right = None
            # if cur already has left child, move to right
            if cur.left:
                cur.right = cur.left
            cur.left = parent
            parent.parent = cur
            cur = parent
        leaf.parent = None
        return leaf
# @lc code=end
