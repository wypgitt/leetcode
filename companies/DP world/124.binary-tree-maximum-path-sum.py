#
# @lc app=leetcode id=124 lang=python3
#
# [124] Binary Tree Maximum Path Sum
#
# https://leetcode.com/problems/binary-tree-maximum-path-sum/description/
#
# algorithms
# Hard (42.63%)
# Likes:    18681
# Dislikes: 795
# Total Accepted:    2.0M
# Total Submissions: 4.7M
# Testcase Example:  "[1,2,3]"
#
# A path in a binary tree is a sequence of nodes where each pair of adjacent
# nodes in the sequence has an edge connecting them. A node can only appear in
# the sequence at most once. Note that the path does not need to pass through
# the root.
#
# The path sum of a path is the sum of the node's values in the path.
#
# Given the root of a binary tree, return the maximum path sum of any non-empty
# path.
#
# Example 1:
#
# Input: root = [1,2,3]
# Output: 6
# Explanation: The optimal path is 2 -> 1 -> 3 with a path sum of 2 + 1 + 3 =
# 6.
#
# Example 2:
#
# Input: root = [-10,9,20,null,null,15,7]
# Output: 42
# Explanation: The optimal path is 15 -> 20 -> 7 with a path sum of 15 + 20 + 7
# = 42.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 3 * 10^4].
#
# -1000 <= Node.val <= 1000
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
    def maxPathSum(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        A path can bend at a node (use both children) but the value returned
        upward can use at most one child (the "gain"), because a parent can
        extend only a single chain.

        Algorithm:
        - DFS returns max gain from this node downward: node.val + max(0, left, right).
        - At each node update global answer with node.val + max(0,left) + max(0,right)
          (the best path that peaks here).
        - Negative child gains are discarded with max(0, ...).

        Complexity: O(n) time, O(h) recursion space.
        """
        best = float("-inf")

        def gain(node: Optional[TreeNode]) -> int:
            nonlocal best
            if not node:
                return 0
            left = max(0, gain(node.left))
            right = max(0, gain(node.right))
            best = max(best, node.val + left + right)
            return node.val + max(left, right)

        gain(root)
        return int(best)
# @lc code=end
