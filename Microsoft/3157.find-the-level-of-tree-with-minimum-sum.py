#
# @lc app=leetcode id=3157 lang=python3
#
# [3157] Find the Level of Tree with Minimum Sum
#
# https://leetcode.com/problems/find-the-level-of-tree-with-minimum-sum/description/
#
# algorithms
# Medium (69.48%)
# Likes:    19
# Dislikes: 3
# Total Accepted:    3.4K
# Total Submissions: 4.9K
# Testcase Example:  "[50,6,2,30,80,7]"
#
#
# Given the root of a binary tree root where each node has a value, return
# the level of the tree that has the minimum sum of values among all the
# levels (in case of a tie, return the lowest level).
#
# Note that the root of the tree is at level 1 and the level of any other
# node is its distance from the root + 1.
#
# Example 1:
#
# Input: root = [50,6,2,30,80,7]
#
# Output: 2
#
# Explanation:
#
# Example 2:
#
# Input: root = [36,17,10,null,null,24]
#
# Output: 3
#
# Explanation:
#
# Example 3:
#
# Input: root = [5,null,5,null,5]
#
# Output: 1
#
# Explanation:
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^5].
#
# 1 <= Node.val <= 10^9
#

# @lc code=start
from collections import deque
from typing import Optional

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

try:
    TreeNode  # type: ignore[name-defined]
except NameError:

    class TreeNode:  # type: ignore[no-redef]
        def __init__(self, val=0, left=None, right=None):
            self.val = val
            self.left = left
            self.right = right


class Solution:
    def minimumLevel(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Return the shallowest level whose node-value sum is minimal (root = 1).

        Algorithm:
        - BFS level order; track (best_sum, best_level) while scanning levels.

        Complexity: O(n) time, O(w) space for the queue width.
        """
        if root is None:
            return 1
        q = deque([root])
        level = 1
        best_level, best_sum = 1, root.val
        while q:
            total = 0
            for _ in range(len(q)):
                node = q.popleft()
                total += node.val
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            if total < best_sum:
                best_sum = total
                best_level = level
            level += 1
        return best_level
# @lc code=end
