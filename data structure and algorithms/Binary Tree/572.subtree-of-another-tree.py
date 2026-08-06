#
# @lc app=leetcode id=572 lang=python3
#
# [572] Subtree of Another Tree
#
# https://leetcode.com/problems/subtree-of-another-tree/description/
#
# algorithms
# Easy (51.99%)
# Likes:    9009
# Dislikes: 607
# Total Accepted:    1.3M
# Total Submissions: 2.5M
# Testcase Example:  "[3,4,5,1,2]"
#
# Given the roots of two binary trees root and subRoot, return true if there is
# a subtree of root with the same structure and node values of subRoot and
# false otherwise.
#
# A subtree of a binary tree tree is a tree that consists of a node in tree and
# all of this node's descendants. The tree tree could also be considered as a
# subtree of itself.
#
# Example 1:
#
# Input: root = [3,4,5,1,2], subRoot = [4,1,2]
# Output: true
#
# Example 2:
#
# Input: root = [3,4,5,1,2,null,null,null,null,0], subRoot = [4,1,2]
# Output: false
#
# Constraints:
#
# The number of nodes in the root tree is in the range [1, 2000].
#
# The number of nodes in the subRoot tree is in the range [1, 1000].
#
# -10^4 <= root.val <= 10^4
#
# -10^4 <= subRoot.val <= 10^4
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
    def isSubtree(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        Check whether some node in root starts a tree identical to subRoot.
        DFS over candidates; at each node try an isSameTree comparison.

        Algorithm:
        - If subRoot is None, True; if root is None, False.
        - Return isSame(root, subRoot) or isSubtree(left) or isSubtree(right).

        Complexity: O(n * m) time worst case, O(h) recursion space.
        """
        if not subRoot:
            return True
        if not root:
            return False

        def same(a: Optional[TreeNode], b: Optional[TreeNode]) -> bool:
            if not a and not b:
                return True
            if not a or not b or a.val != b.val:
                return False
            return same(a.left, b.left) and same(a.right, b.right)

        if same(root, subRoot):
            return True
        return self.isSubtree(root.left, subRoot) or self.isSubtree(root.right, subRoot)

    def isSubtreeSerialize(self, root: Optional[TreeNode], subRoot: Optional[TreeNode]) -> bool:
        """
        Interview explanation:
        Serialize both trees with null markers and delimiters so subtree
        checks reduce to substring search on the preorder strings. Classic
        alternate when you want string algorithms (or KMP) instead of nested DFS.

        Algorithm:
        - Preorder serialize with sentinels (e.g. '#') and value delimiters.
        - Return serialize(subRoot) in serialize(root).

        Complexity: O(n + m) time and space for serialization (+ substring).
        """
        def serialize(node: Optional[TreeNode]) -> str:
            if not node:
                return "#,"
            return f"^{node.val}," + serialize(node.left) + serialize(node.right)

        return serialize(subRoot) in serialize(root)
# @lc code=end

