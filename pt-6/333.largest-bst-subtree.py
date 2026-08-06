#
# @lc app=leetcode id=333 lang=python3
#
# [333] Largest BST Subtree
#
# https://leetcode.com/problems/largest-bst-subtree/description/
#
# algorithms
# Medium (45.92%)
# Likes:    1570
# Dislikes: 148
# Total Accepted:    129.8K
# Total Submissions: 282.7K
# Testcase Example:  "[10,5,15,1,8,null,7]"
#
#
# Given the root of a binary tree, find the largest subtree, which is also
# a Binary Search Tree (BST), where the largest means subtree has the
# largest number of nodes.
#
# A Binary Search Tree (BST) is a tree in which all the nodes follow the
# below-mentioned properties:
#
# The left subtree values are less than the value of their parent (root)
# node's value.
#
# The right subtree values are greater than the value of their parent
# (root) node's value.
#
# Note: A subtree must include all of its descendants.
#
# Example 1:
#
# Input: root = [10,5,15,1,8,null,7]
# Output: 3
# Explanation: The Largest BST Subtree in this case is the highlighted
# one. The return value is the subtree's size, which is 3.
#
# Example 2:
#
# Input: root = [4,2,7,2,3,5,null,2,null,null,null,null,null,1]
# Output: 2
#
# Constraints:
#
# The number of nodes in the tree is in the range [0, 10^4].
#
# -10^4 <= Node.val <= 10^4
#
# Follow up: Can you figure out ways to solve it with O(n) time
# complexity?
#
# @lc code=start
from typing import Optional, Tuple

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def largestBSTSubtree(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Postorder validate: each subtree returns (is_bst, size, min, max).
        A node forms a BST if both children are BSTs and
        left.max < node.val < right.max; track global max size.

        Algorithm:
        - Recurse left/right; combine with current node.
        - Empty tree is BST of size 0 with min=+inf, max=-inf.
        - Update answer whenever a valid BST is found.

        Complexity: O(n) time, O(h) space.
        """
        self.best = 0

        def dfs(node: Optional[TreeNode]) -> Tuple[bool, int, float, float]:
            if not node:
                return True, 0, float("inf"), float("-inf")
            l_ok, l_sz, l_mn, l_mx = dfs(node.left)
            r_ok, r_sz, r_mn, r_mx = dfs(node.right)
            if l_ok and r_ok and l_mx < node.val < r_mn:
                size = l_sz + r_sz + 1
                self.best = max(self.best, size)
                return True, size, min(l_mn, node.val), max(r_mx, node.val)
            return False, 0, 0, 0

        dfs(root)
        return self.best
# @lc code=end
