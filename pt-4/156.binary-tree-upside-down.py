"""
Approach: Iteratively rotate pointers along the original left spine.
Data structure: three pointers track the previous parent, previous right child, and current node.
Interview logic: each current node becomes the root of the processed part; current.left becomes the former right sibling, and current.right becomes the former parent.
Complexity: O(h) time for left-spine height h, O(1) space.
Tests and edge cases: empty tree; single node; valid LeetCode shape where right nodes are leaves or paired with left siblings.
"""
from __future__ import annotations
from typing import Optional

# @lc code=start
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def upsideDownBinaryTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        parent = None
        parent_right = None
        cur = root
        while cur:
            next_left = cur.left
            cur.left = parent_right
            parent_right = cur.right
            cur.right = parent
            parent = cur
            cur = next_left
        return parent
# @lc code=end
