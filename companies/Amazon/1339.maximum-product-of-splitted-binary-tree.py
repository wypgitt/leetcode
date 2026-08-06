#
# @lc app=leetcode id=1339 lang=python3
#
# [1339] Maximum Product of Splitted Binary Tree
#
# https://leetcode.com/problems/maximum-product-of-splitted-binary-tree/description/
#
# algorithms
# Medium (55.76%)
# Likes:    3594
# Dislikes: 122
# Total Accepted:    263K
# Total Submissions: 471K
# Testcase Example:  "[1,2,3,4,5,6]"
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
# Example 1:
#
# Input: root = [1,2,3,4,5,6]
# Output: 110
# Explanation: Remove the red edge and get 2 binary trees with sum 11 and 10.
# Their product is 110 (11*10)
#
# Example 2:
#
# Input: root = [1,null,2,3,4,null,null,5,6]
# Output: 90
# Explanation: Remove the red edge and get 2 binary trees with sum 15 and
# 6.Their product is 90 (15*6)
#
# Constraints:
#
# The number of nodes in the tree is in the range [2, 5 * 10^4].
#
# 1 <= Node.val <= 10^4
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
    def maxProduct(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Remove one edge -> two subtrees; maximize product of subtree sums.
        Total sum S; for each subtree sum t, product t*(S-t). One DFS for S,
        second (or same collecting) track max product.

        Algorithm:
        - Compute total; dfs returns subtree sum and updates best t*(S-t).

        Complexity: O(n) time, O(h) space.
        """
        MOD = 10**9 + 7

        def total(node):
            if not node:
                return 0
            return node.val + total(node.left) + total(node.right)

        S = total(root)
        best = 0

        def dfs(node):
            nonlocal best
            if not node:
                return 0
            t = node.val + dfs(node.left) + dfs(node.right)
            best = max(best, t * (S - t))
            return t

        dfs(root)
        return best % MOD
# @lc code=end

