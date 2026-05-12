#
# @lc app=leetcode id=1339 lang=python3
#
# [1339] Maximum Product of Splitted Binary Tree
#
# https://leetcode.com/problems/maximum-product-of-splitted-binary-tree/description/
#
# algorithms
# Medium (55.69%)
# Likes:    3584
# Dislikes: 122
# Total Accepted:    259K
# Total Submissions: 465.1K
# Testcase Example:  '[1,2,3,4,5,6]'
#
# Given the root of a binary tree, split the binary tree into two subtrees by
# removing one edge such that the product of the sums of the subtrees is
# maximized.
# 
# Return the maximum product of the sums of the two subtrees. Since the answer
# may be too large, return it modulo 10^9 + 7.
# 
# Note that you need to maximize the answer before taking the mod and not after
# taking it.
# 
# 
# Example 1:
# 
# 
# Input: root = [1,2,3,4,5,6]
# Output: 110
# Explanation: Remove the red edge and get 2 binary trees with sum 11 and 10.
# Their product is 110 (11*10)
# 
# 
# Example 2:
# 
# 
# Input: root = [1,null,2,3,4,null,null,5,6]
# Output: 90
# Explanation: Remove the red edge and get 2 binary trees with sum 15 and
# 6.Their product is 90 (15*6)
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [2, 5 * 10^4].
# 1 <= Node.val <= 10^4
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import Optional


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def maxProduct(self, root: Optional[TreeNode]) -> int:
        MOD = 10**9 + 7

        def subtree_sum(node: Optional[TreeNode]) -> int:
            if node is None:
                return 0
            return node.val + subtree_sum(node.left) + subtree_sum(node.right)

        total_sum = subtree_sum(root)
        best = 0

        def find_best(node: Optional[TreeNode]) -> int:
            nonlocal best
            if node is None:
                return 0

            current = node.val + find_best(node.left) + find_best(node.right)
            best = max(best, current * (total_sum - current))
            return current

        find_best(root)
        return best % MOD
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# Removing one edge separates the tree into a subtree and the rest of the tree.
# If a subtree has sum `s` and total tree sum is `T`, the product is
# `s * (T - s)`. So compute every subtree sum and maximize that product.
#
# Why two DFS passes:
# The product needs the total sum `T`, so the first DFS computes it. The second
# DFS recomputes subtree sums and updates the best product.
#
# Data structure:
# Recursion performs postorder traversal. No extra map is required because each
# subtree sum can be returned to its parent as soon as it is computed.
#
# Edge cases:
# - Single node: no meaningful split, product remains 0.
# - Very large product: take modulo only at the end because modulo can change
#   comparisons.
# - Skewed tree: recursion depth is O(n), still the same logic.
#
# Complexity:
# - Time: O(n), two linear DFS passes.
# - Space: O(h), recursion stack height.
