#
# @lc app=leetcode id=1305 lang=python3
#
# [1305] All Elements in Two Binary Search Trees
#
# https://leetcode.com/problems/all-elements-in-two-binary-search-trees/description/
#
# algorithms
# Medium (80.26%)
# Likes:    3193
# Dislikes: 99
# Total Accepted:    263.7K
# Total Submissions: 328.6K
# Testcase Example:  '[2,1,4]\n[1,0,3]'
#
# Given two binary search trees root1 and root2, return a list containing all
# the integers from both trees sorted in ascending order.
# 
# 
# Example 1:
# 
# 
# Input: root1 = [2,1,4], root2 = [1,0,3]
# Output: [0,1,1,2,3,4]
# 
# 
# Example 2:
# 
# 
# Input: root1 = [1,null,8], root2 = [8,1]
# Output: [1,1,8,8]
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in each tree is in the range [0, 5000].
# -10^5 <= Node.val <= 10^5
# 
# 
#

# @lc code=start
from __future__ import annotations

from typing import List, Optional


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def getAllElements(self, root1: Optional[TreeNode], root2: Optional[TreeNode]) -> List[int]:
        def inorder(root: Optional[TreeNode], values: List[int]) -> None:
            if root is None:
                return

            inorder(root.left, values)
            values.append(root.val)
            inorder(root.right, values)

        first: List[int] = []
        second: List[int] = []
        inorder(root1, first)
        inorder(root2, second)

        merged: List[int] = []
        i = j = 0

        while i < len(first) and j < len(second):
            if first[i] <= second[j]:
                merged.append(first[i])
                i += 1
            else:
                merged.append(second[j])
                j += 1

        merged.extend(first[i:])
        merged.extend(second[j:])
        return merged
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# A BST's inorder traversal produces values in sorted order. The problem then
# becomes the classic merge step from merge sort: merge two sorted arrays into
# one sorted answer.
#
# Why not just collect and sort everything?
# That works, but it spends O((m+n) log(m+n)) time. Using the BST property gives
# two already sorted lists and a linear merge, so the main work is O(m+n).
#
# Data structures:
# - Two lists store the inorder traversals.
# - A third list stores the merged output.
#
# Walkthrough:
# 1. Traverse `root1` inorder into `first`.
# 2. Traverse `root2` inorder into `second`.
# 3. Use two pointers to append the smaller current value.
# 4. Append the remaining suffix from whichever list still has values.
#
# Edge cases:
# - One tree is empty: its inorder list is empty, and the answer is the other
#   list.
# - Duplicate values: use `<=` so duplicates from both lists are preserved.
# - Both trees empty: returns an empty list.
#
# Complexity:
# - Time: O(m+n), where m and n are the sizes of the two trees.
# - Space: O(m+n) for the two traversals and answer, plus O(h1+h2) recursion
#   stack.
#
# Improvement:
# We could avoid storing both full traversals by using two iterative inorder
# generators and merging lazily, but the current version is simpler and well
# within the problem constraints.
