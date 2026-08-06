#
# @lc app=leetcode id=783 lang=python3
#
# [783] Minimum Distance Between BST Nodes
#
# https://leetcode.com/problems/minimum-distance-between-bst-nodes/description/
#
# algorithms
# Easy (61.72%)
# Likes:    3709
# Dislikes: 437
# Total Accepted:    343K
# Total Submissions: 555K
# Testcase Example:  "[4,2,6,1,3]"
#
# Given the root of a Binary Search Tree (BST), return the minimum difference
# between the values of any two different nodes in the tree.
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
# The number of nodes in the tree is in the range [2, 100].
#
# 0 <= Node.val <= 10^5
#
# Note: This question is the same as 530:
# https://leetcode.com/problems/minimum-absolute-difference-in-bst/
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
    def minDiffInBST(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        BST inorder yields sorted values; minimum difference between any two
        nodes is the min gap between consecutive inorder values.

        Algorithm:
        - Inorder DFS; track prev value; update ans = min(ans, node.val - prev).

        Complexity: O(n) time, O(h) space.
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
        return int(self.ans)
# @lc code=end

