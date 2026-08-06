#
# @lc app=leetcode id=156 lang=python3
#
# [156] Binary Tree Upside Down
#
# Problem (one level):
#   Given a node with left child L and right child R, “flip” this triangle so that
#   L becomes the new root, R becomes L’s new left child, and the old root becomes
#   L’s new right child.
#
# Why iteration along the left spine works:
#   The guarantee (every right node has a left sibling and no children) means the
#   tree is effectively a chain along the left edge with optional right “buds”.
#   Processing from the original root downward is the same as flipping level by
#   level from top to bottom; each step only needs the previous parent and that
#   parent’s old right child to wire the new left/right pointers.
#
# Variables:
#   curr          — node we are rewiring this iteration (walking left).
#   parent        — the node that was above curr in the original tree; becomes
#                   curr’s new right child after the flip at this step.
#   parent_right  — the old right child of `parent` (sibling of curr in the
#                   original tree); becomes curr’s new left child. For the first
#                   node we process, there is no such sibling yet, so None.

# @lc code=start
from typing import Optional

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def upsideDownBinaryTree(self, root: Optional[TreeNode]) -> Optional[TreeNode]:
        curr = root
        parent = None
        parent_right = None

        while curr:
            # Save children before we overwrite pointers.
            left = curr.left
            right = curr.right

            # Apply the upside-down rule for this node:
            # new left  = old right sibling of the node above (None on first step)
            # new right = old parent
            curr.left = parent_right
            curr.right = parent

            # Advance: next node down the left spine; carry flip context upward.
            parent_right = right
            parent = curr
            curr = left

        # Last processed node was the old leftmost node — it is the new root.
        return parent

# @lc code=end

