#
# @lc app=leetcode id=671 lang=python3
#
# [671] Second Minimum Node In a Binary Tree
#
# https://leetcode.com/problems/second-minimum-node-in-a-binary-tree/description/
#
# algorithms
# Easy (46.29%)
# Likes:    2017
# Dislikes: 1905
# Total Accepted:    251K
# Total Submissions: 542K
# Testcase Example:  "[2,2,5,null,null,5,7]"
#
# Given a non-empty special binary tree consisting of nodes with the
# non-negative value, where each node in this tree has exactly two or zero
# sub-node. If the node has two sub-nodes, then this node's value is the
# smaller value among its two sub-nodes. More formally, the property root.val =
# min(root.left.val, root.right.val) always holds.
#
# Given such a binary tree, you need to output the second minimum value in the
# set made of all the nodes' value in the whole tree.
#
# If no such second minimum value exists, output -1 instead.
#
# Example 1:
#
# Input: root = [2,2,5,null,null,5,7]
# Output: 5
# Explanation: The smallest value is 2, the second smallest value is 5.
#
# Example 2:
#
# Input: root = [2,2,2]
# Output: -1
# Explanation: The smallest value is 2, but there isn't any second smallest
# value.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 25].
#
# 1 <= Node.val <= 2^31 - 1
#
# root.val == min(root.left.val, root.right.val) for each internal node of the
# tree.
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
    def findSecondMinimumValue(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Special tree: 0 or 2 children; parent.val = min(children). Root is the
        global minimum; answer is smallest value strictly greater than root
        (or -1).

        Algorithm:
        - DFS: explore only nodes equal to first min (larger subtrees cannot
          hide a smaller second); track min > first.

        Complexity: O(n) time, O(h) space.
        """
        if not root:
            return -1
        first = root.val
        second = float("inf")

        def dfs(node: Optional[TreeNode]) -> None:
            nonlocal second
            if not node:
                return
            if first < node.val < second:
                second = node.val
            elif node.val == first:
                dfs(node.left)
                dfs(node.right)

        dfs(root)
        return int(second) if second < float("inf") else -1
# @lc code=end
