#
# @lc app=leetcode id=2313 lang=python3
#
# [2313] Minimum Flips in Binary Tree to Get Result
#
# https://leetcode.com/problems/minimum-flips-in-binary-tree-to-get-result/description/
#
# algorithms
# Hard (57.00%)
# Likes:    115
# Dislikes: 2
# Total Accepted:    5.3K
# Total Submissions: 9.3K
# Testcase Example:  "[3,5,4,2,null,1,1,1,0]\ntrue"
#
#
# You are given the root of a binary tree with the following properties:
#
# Leaf nodes have either the value 0 or 1, representing false and true
# respectively.
#
# Non-leaf nodes have either the value 2, 3, 4, or 5, representing the
# boolean operations OR, AND, XOR, and NOT, respectively.
#
# You are also given a boolean result, which is the desired result of the
# evaluation of the root node.
#
# The evaluation of a node is as follows:
#
# If the node is a leaf node, the evaluation is the value of the node,
# i.e. true or false.
#
# Otherwise, evaluate the node's children and apply the boolean operation
# of its value with the children's evaluations.
#
# In one operation, you can flip a leaf node, which causes a false node to
# become true, and a true node to become false.
#
# Return the minimum number of operations that need to be performed such
# that the evaluation of root yields result. It can be shown that there is
# always a way to achieve result.
#
# A leaf node is a node that has zero children.
#
# Note: NOT nodes have either a left child or a right child, but other
# non-leaf nodes have both a left child and a right child.
#
# Example 1:
#
# Input: root = [3,5,4,2,null,1,1,1,0], result = true
# Output: 2
# Explanation:
# It can be shown that a minimum of 2 nodes have to be flipped to make the
# root of the tree
# evaluate to true. One way to achieve this is shown in the diagram above.
#
# Example 2:
#
# Input: root = [0], result = false
# Output: 0
# Explanation:
# The root of the tree already evaluates to false, so 0 nodes have to be
# flipped.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^5].
#
# 0 <= Node.val <= 5
#
# OR, AND, and XOR nodes have 2 children.
#
# NOT nodes have 1 child.
#
# Leaf nodes have a value of 0 or 1.
#
# Non-leaf nodes have a value of 2, 3, 4, or 5.
#
# @lc code=start
from typing import Optional
from math import inf

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def minimumFlips(self, root: Optional['TreeNode'], result: bool) -> int:
        """
        Interview explanation:
        Boolean expression tree: leaves 0/1; ops OR=2, AND=3, XOR=4, NOT=5.
        Min leaf flips so root evaluates to `result`.

        Algorithm:
        - DFS returns (min flips for False, min flips for True) for each subtree.
        - Combine children per operator; NOT swaps; leaves need 0/1 flip.

        Complexity: O(n) time, O(h) space.
        """
        def dfs(node):
            if node is None:
                return inf, inf
            x = node.val
            if x in (0, 1):
                return (x, x ^ 1)  # cost to make False, True
            if x == 5:  # NOT
                child = node.left or node.right
                f, t = dfs(child)
                return t, f
            lf, lt = dfs(node.left)
            rf, rt = dfs(node.right)
            if x == 2:  # OR
                return lf + rf, min(lf + rt, lt + rf, lt + rt)
            if x == 3:  # AND
                return min(lf + rf, lf + rt, lt + rf), lt + rt
            # XOR
            return min(lf + rf, lt + rt), min(lf + rt, lt + rf)

        return dfs(root)[int(result)]

    def minimumFlips_dfs(self, root: Optional['TreeNode'], result: bool) -> int:
        """
        Interview explanation:
        Tree DP via DFS (same as primary).

        Algorithm:
        - Return pair of costs for false/true targets.

        Complexity: O(n) time, O(h) space.
        """
        return self.minimumFlips(root, result)
# @lc code=end
