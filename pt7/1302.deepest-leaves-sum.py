#
# @lc app=leetcode id=1302 lang=python3
#
# [1302] Deepest Leaves Sum
#
# https://leetcode.com/problems/deepest-leaves-sum/description/
#
# algorithms
# Medium (86.53%)
# Likes:    4847
# Dislikes: 127
# Total Accepted:    407.4K
# Total Submissions: 470.8K
# Testcase Example:  '[1,2,3,4,5,null,6,7,null,null,null,null,8]'
#
# Given the root of a binary tree, return the sum of values of its deepest
# leaves.
# 
# Example 1:
# 
# 
# Input: root = [1,2,3,4,5,null,6,7,null,null,null,null,8]
# Output: 15
# 
# 
# Example 2:
# 
# 
# Input: root = [6,7,8,2,7,1,3,9,null,1,4,null,null,null,5]
# Output: 19
# 
# 
# 
# Constraints:
# 
# 
# The number of nodes in the tree is in the range [1, 10^4].
# 1 <= Node.val <= 100
# 
# 
#

# @lc code=start
from __future__ import annotations

from collections import deque
from typing import Optional


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def deepestLeavesSum(self, root: Optional[TreeNode]) -> int:
        if root is None:
            return 0

        queue = deque([root])
        level_sum = 0

        while queue:
            level_sum = 0
            for _ in range(len(queue)):
                node = queue.popleft()
                level_sum += node.val

                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)

        return level_sum
# @lc code=end

#
# Interview explanation
# ---------------------
# Idea:
# We need the sum of the deepest level only. A level-order traversal naturally
# visits the tree one depth at a time, so we keep replacing `level_sum` with the
# sum of the current layer. When the BFS finishes, the last computed layer is
# exactly the deepest leaves.
#
# Data structure:
# `deque` is the right queue for BFS because popping from the left is O(1).
# A Python list would make `pop(0)` O(n), which is unnecessary overhead.
#
# Walkthrough:
# 1. Put the root in the queue.
# 2. For each BFS layer, reset `level_sum` to 0.
# 3. Consume exactly the nodes that were in the queue at the start of that
#    layer, add their values, and enqueue their children.
# 4. Return the final `level_sum`.
#
# Edge cases:
# - Empty tree: return 0 defensively, even though LeetCode gives a non-empty
#   tree for this problem.
# - Single node: one BFS layer, so the answer is the root value.
# - Skewed tree: still works because each layer contains one node.
#
# Complexity:
# - Time: O(n), every node is visited once.
# - Space: O(w), where w is the maximum width of the tree held in the queue.
#
# Tests to discuss:
# - [1,2,3,4,5,null,6,7,null,null,null,null,8] -> 15.
# - [6,7,8,2,7,1,3,9,null,1,4,null,null,null,5] -> 19.
# - [1] -> 1.
