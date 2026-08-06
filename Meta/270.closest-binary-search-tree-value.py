#
# @lc app=leetcode id=270 lang=python3
#
# [270] Closest Binary Search Tree Value
#
# https://leetcode.com/problems/closest-binary-search-tree-value/description/
#
# algorithms
# Easy (49.14%)
# Likes:    1903
# Dislikes: 166
# Total Accepted:    456.7K
# Total Submissions: 929.4K
# Testcase Example:  "[4,2,5,1,3]\n3.714286"
#
#
# Given the root of a binary search tree and a target value, return the
# value in the BST that is closest to the target. If there are multiple
# answers, print the smallest.
#
# Example 1:
#
# Input: root = [4,2,5,1,3], target = 3.714286
# Output: 4
#
# Example 2:
#
# Input: root = [1], target = 4.428571
# Output: 1
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# 0 <= Node.val <= 10^9
#
# -10^9 <= target <= 10^9
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
    def closestValue(self, root: Optional[TreeNode], target: float) -> int:
        """
        Interview explanation:
        Walk the BST toward target while tracking the closest value seen.
        Prefer the smaller value on ties (common LeetCode convention).

        Algorithm:
        - Start at root; compare |node.val - target| with best.
        - Go left if target < node.val else right (standard BST search).
        - Return the recorded closest integer.

        Complexity: O(h) time, O(1) space.
        """
        closest = root.val
        node = root
        while node:
            if abs(node.val - target) < abs(closest - target) or (
                abs(node.val - target) == abs(closest - target) and node.val < closest
            ):
                closest = node.val
            node = node.left if target < node.val else node.right
        return closest
# @lc code=end

