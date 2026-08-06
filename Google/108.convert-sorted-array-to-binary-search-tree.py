#
# @lc app=leetcode id=108 lang=python3
#
# [108] Convert Sorted Array to Binary Search Tree
#
# https://leetcode.com/problems/convert-sorted-array-to-binary-search-tree/description/
#
# algorithms
# Easy (75.94%)
# Likes:    12032
# Dislikes: 654
# Total Accepted:    1.8M
# Total Submissions: 2.4M
# Testcase Example:  "[-10,-3,0,5,9]"
#
# Given an integer array nums where the elements are sorted in ascending order,
# convert it to a height-balanced binary search tree.
#
# Example 1:
#
# Input: nums = [-10,-3,0,5,9]
# Output: [0,-3,9,-10,null,5]
# Explanation: [0,-10,5,null,-3,null,9] is also accepted:
#
# Example 2:
#
# Input: nums = [1,3]
# Output: [3,1]
# Explanation: [1,null,3] and [3,1] are both height-balanced BSTs.
#
# Constraints:
#
# 1 <= nums.length <= 10^4
#
# -10^4 <= nums[i] <= 10^4
#
# nums is sorted in a strictly increasing order.
#

# @lc code=start
from typing import List, Optional
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def sortedArrayToBST(self, nums: List[int]) -> Optional[TreeNode]:
        """
        Interview explanation:
        A sorted array is the inorder sequence of a BST. Choosing the middle
        element as root keeps left and right halves balanced, producing a
        height-balanced BST.

        Algorithm:
        - Recursively build on inclusive index range [lo, hi].
        - Mid becomes the root; left half builds left subtree, right half right.

        Complexity: O(n) time, O(log n) recursion space for a balanced tree.
        """
        def build(lo: int, hi: int) -> Optional[TreeNode]:
            if lo > hi:
                return None
            mid = (lo + hi) // 2
            node = TreeNode(nums[mid])
            node.left = build(lo, mid - 1)
            node.right = build(mid + 1, hi)
            return node

        return build(0, len(nums) - 1)
# @lc code=end
