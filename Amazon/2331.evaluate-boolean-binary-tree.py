#
# @lc app=leetcode id=2331 lang=python3
#
# [2331] Evaluate Boolean Binary Tree
#
# https://leetcode.com/problems/evaluate-boolean-binary-tree/description/
#
# algorithms
# Easy (82.37%)
# Likes:    1568
# Dislikes: 44
# Total Accepted:    230.6K
# Total Submissions: 280K
# Testcase Example:  "[2,1,3,null,null,0,1]"
#
# You are given the root of a full binary tree with the following properties:
#
#
# Leaf nodes have either the value 0 or 1, where 0 represents False and 1
# represents True.
#
#
# Non-leaf nodes have either the value 2 or 3, where 2 represents the boolean OR
# and 3 represents the boolean AND.
#
# The evaluation of a node is as follows:
#
#
# If the node is a leaf node, the evaluation is the value of the node, i.e. True
# or False.
#
#
# Otherwise, evaluate the node's two children and apply the boolean operation of
# its value with the children's evaluations.
#
# Return the boolean result of evaluating the root node.
#
# A full binary tree is a binary tree where each node has either 0 or 2
# children.
#
# A leaf node is a node that has zero children.
#
#
#
# Example 1:
#
# Input: root = [2,1,3,null,null,0,1]
# Output: true
# Explanation: The above diagram illustrates the evaluation process.
# The AND node evaluates to False AND True = False.
# The OR node evaluates to True OR False = True.
# The root node evaluates to True, so we return true.
#
# Example 2:
#
# Input: root = [0]
# Output: false
# Explanation: The root node is a leaf node and it evaluates to false, so we
# return false.
#
#
#
# Constraints:
#
#
# The number of nodes in the tree is in the range [1, 1000].
#
#
# 0 <= Node.val <= 3
#
#
# Every node has either 0 or 2 children.
#
#
# Leaf nodes have a value of 0 or 1.
#
#
# Non-leaf nodes have a value of 2 or 3.
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
    def evaluateTree(self, root: Optional['TreeNode']) -> bool:
        """
        Interview explanation:
        Full binary tree: leaves 0/1; non-leaves 2=OR, 3=AND. Evaluate.

        Algorithm:
        - Recurse: leaf -> bool(val); OR/AND combine children.

        Complexity: O(n) time, O(h) space.
        """
        if root.val < 2:
            return bool(root.val)
        left = self.evaluateTree(root.left)
        right = self.evaluateTree(root.right)
        return (left or right) if root.val == 2 else (left and right)

    def evaluateTree_dfs(self, root: Optional['TreeNode']) -> bool:
        """
        Interview explanation:
        DFS recursive evaluation (same as primary).

        Algorithm:
        - Post-order evaluate boolean ops.

        Complexity: O(n) time, O(h) space.
        """
        return self.evaluateTree(root)
# @lc code=end
