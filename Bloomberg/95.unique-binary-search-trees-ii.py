#
# @lc app=leetcode id=95 lang=python3
#
# [95] Unique Binary Search Trees II
#
# https://leetcode.com/problems/unique-binary-search-trees-ii/description/
#
# algorithms
# Medium (62.42%)
# Likes:    7963
# Dislikes: 584
# Total Accepted:    582.9K
# Total Submissions: 933.8K
# Testcase Example:  '3'
#
# Given an integer n, return all the structurally unique BST's (binary search
# trees), which has exactly n nodes of unique values from 1 to n. Return the
# answer in any order.
# 
# 
# Example 1:
# 
# 
# Input: n = 3
# Output:
# [[1,null,2,null,3],[1,null,3,2],[2,1,3],[3,1,null,null,2],[3,2,null,1]]
# 
# 
# Example 2:
# 
# 
# Input: n = 1
# Output: [[1]]
# 
# 
# 
# Constraints:
# 
# 
# 1 <= n <= 8
# 
# 
#

# @lc code=start
from typing import List, Optional
from functools import lru_cache

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def generateTrees(self, n: int) -> List[Optional[TreeNode]]:
        """
        Interview explanation:
        For every possible root value, all values smaller than it must appear in
        the left subtree and all larger values in the right subtree. Recursively
        generate every left and right subtree, then combine each pair under a new
        root. This mirrors the Catalan recurrence, but returns actual trees.

        Edge cases and tests:
        - n=1 returns one single-node tree.
        - Empty subtree is represented by [None] so leaf combinations work.
        - The number of trees for n=3 is 5.

        Complexity: O(C_n * n) time and space for C_n generated BSTs. Recursion
        depth is O(n). Cached subtree lists reduce repeated generation.
        """
        @lru_cache(None)
        def build(lo: int, hi: int) -> tuple[Optional[TreeNode], ...]:
            if lo > hi:
                return (None,)
            trees = []
            for root_val in range(lo, hi + 1):
                for left in build(lo, root_val - 1):
                    for right in build(root_val + 1, hi):
                        root = TreeNode(root_val)
                        root.left = left
                        root.right = right
                        trees.append(root)
            return tuple(trees)

        return list(build(1, n))
# @lc code=end


