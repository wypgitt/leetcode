#
# @lc app=leetcode id=776 lang=python3
#
# [776] Split BST
#
# https://leetcode.com/problems/split-bst/description/
#
# algorithms
# Medium (82.13%)
# Likes:    1093
# Dislikes: 105
# Total Accepted:    112.8K
# Total Submissions: 137.3K
# Testcase Example:  "[4,2,6,1,3,5,7]\n2"
#
#
# Given the root of a binary search tree (BST) and an integer target,
# split the tree into two subtrees where the first subtree has nodes that
# are all smaller or equal to the target value, while the second subtree
# has all nodes that are greater than the target value. It is not
# necessarily the case that the tree contains a node with the value
# target.
#
# Additionally, most of the structure of the original tree should remain.
# Formally, for any child c with parent p in the original tree, if they
# are both in the same subtree after the split, then node c should still
# have the parent p.
#
# Return an array of the two roots of the two subtrees in order.
#
# Example 1:
#
# Input: root = [4,2,6,1,3,5,7], target = 2
# Output: [[2,1],[4,3,6,null,null,5,7]]
#
# Example 2:
#
# Input: root = [1], target = 1
# Output: [[1],[]]
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 50].
#
# 0 <= Node.val, target <= 1000
#
# @lc code=start
from typing import List, Optional

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
    def splitBST(self, root: Optional[TreeNode], target: int) -> List[Optional[TreeNode]]:
        """
        Interview explanation:
        Premium. Split BST into two trees: all nodes <= target, and all > target.
        Recurse by BST order: if root.val <= target, root stays in left tree and
        we split root.right (some of right may still be <= target); attach the
        >target part as root.right. Symmetrically if root.val > target.

        Algorithm:
        - If not root: return [None, None]
        - If root.val <= target:
            left, right = split(root.right, target)
            root.right = left
            return [root, right]
        - Else:
            left, right = split(root.left, target)
            root.left = right
            return [left, root]

        Complexity: O(h) time, O(h) space.
        """
        if not root:
            return [None, None]
        if root.val <= target:
            left, right = self.splitBST(root.right, target)
            root.right = left
            return [root, right]
        left, right = self.splitBST(root.left, target)
        root.left = right
        return [left, root]
# @lc code=end

