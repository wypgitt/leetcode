#
# @lc app=leetcode id=1214 lang=python3
#
# [1214] Two Sum BSTs
#
# https://leetcode.com/problems/two-sum-bsts/description/
#
# algorithms
# Medium (68.18%)
# Likes:    579
# Dislikes: 46
# Total Accepted:    61.6K
# Total Submissions: 90.4K
# Testcase Example:  '[2,1,4]\n[1,0,3]\n5'
#
# Given the roots of two binary search trees, root1 and root2, return true if
# and only if there is a node in the first tree and a node in the second tree
# whose values sum up to a given integer target.
# 
# 
# Example 1:
# 
# 
# Input: root1 = [2,1,4], root2 = [1,0,3], target = 5
# Output: true
# Explanation: 2 and 3 sum up to 5.
# 
# 
# Example 2:
# 
# 
# Input: root1 = [0,-10,10], root2 = [5,1,7,0,2], target = 18
# Output: false
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in each tree is in the range [1, 5000].
# -10^9 <= Node.val, target <= 10^9
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
    def twoSumBSTs(self, root1: Optional[TreeNode], root2: Optional[TreeNode], target: int) -> bool:
        values = set()

        def collect(node):
            if not node:
                return
            values.add(node.val)
            collect(node.left)
            collect(node.right)

        def search(node):
            if not node:
                return False
            if target - node.val in values:
                return True
            return search(node.left) or search(node.right)

        collect(root1)
        return search(root2)
# @lc code=end

# Explanation
# -----------
# Store every value from the first BST in a hash set, then traverse the second
# BST and ask whether target - node.val exists in that set. This uses the BSTs
# as binary trees; sorted order is not necessary because the hash set gives
# O(1)-average complement lookup.
#
# The hash set is chosen because the question is existence, not ordering. A
# sorted two-pointer traversal is possible, but it needs two controlled
# iterators. The set solution is simpler and very reliable in interviews.
#
# Edge cases: either tree can be empty; duplicate values are harmless because
# the complement only needs to exist in the other tree; negative values work
# the same as positive values.
#
# Tests to discuss: one complement pair across the roots; no pair; pair where
# one value is negative; one empty tree.
#
# Time complexity: O(n + m), where n and m are the tree sizes.
# Space complexity: O(n) for the first tree's values, plus recursion stack.
