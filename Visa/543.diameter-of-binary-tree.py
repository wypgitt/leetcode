#
# @lc app=leetcode id=543 lang=python3
#
# [543] Diameter of Binary Tree
#
# https://leetcode.com/problems/diameter-of-binary-tree/description/
#
# algorithms
# Easy (66.02%)
# Likes:    15888
# Dislikes: 1259
# Total Accepted:    2.6M
# Total Submissions: 4.0M
# Testcase Example:  "[1,2,3,4,5]"
#
# Given the root of a binary tree, return the length of the diameter of the
# tree.
#
# The diameter of a binary tree is the length of the longest path between any
# two nodes in a tree. This path may or may not pass through the root.
#
# The length of a path between two nodes is represented by the number of edges
# between them.
#
# Example 1:
#
# Input: root = [1,2,3,4,5]
# Output: 3
# Explanation: 3 is the length of the path [4,2,1,3] or [5,2,1,3].
#
# Example 2:
#
# Input: root = [1,2]
# Output: 1
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# -100 <= Node.val <= 100
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
    def diameterOfBinaryTree(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Diameter through a node is left_height + right_height (edges). DFS
        returns height while updating global max diameter.

        Algorithm:
        - dfs(node) returns height; ans = max(ans, L+R); return 1+max(L,R).

        Complexity: O(n) time, O(h) space.
        """
        self.ans = 0

        def dfs(node: Optional[TreeNode]) -> int:
            if not node:
                return 0
            left = dfs(node.left)
            right = dfs(node.right)
            self.ans = max(self.ans, left + right)
            return 1 + max(left, right)

        dfs(root)
        return self.ans
# @lc code=end

