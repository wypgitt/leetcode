#
# @lc app=leetcode id=1161 lang=python3
#
# [1161] Maximum Level Sum of a Binary Tree
#
# https://leetcode.com/problems/maximum-level-sum-of-a-binary-tree/description/
#
# algorithms
# Medium (70.03%)
# Likes:    4163
# Dislikes: 117
# Total Accepted:    591K
# Total Submissions: 844K
# Testcase Example:  "[1,7,0,7,-8,null,null]"
#
# Given the root of a binary tree, the level of its root is 1, the level of its
# children is 2, and so on.
#
# Return the smallest level x such that the sum of all the values of nodes at
# level x is maximal.
#
# Example 1:
#
# Input: root = [1,7,0,7,-8,null,null]
# Output: 2
# Explanation:
# Level 1 sum = 1.
# Level 2 sum = 7 + 0 = 7.
# Level 3 sum = 7 + -8 = -1.
# So we return the level with the maximum sum which is level 2.
#
# Example 2:
#
# Input: root = [989,null,10250,98693,-89388,null,null,null,-32127]
# Output: 2
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# -10^5 <= Node.val <= 10^5
#

# @lc code=start
from typing import Optional, List, Deque
from collections import deque


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def maxLevelSum(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Return the smallest 1-indexed level with maximum sum of node values.
        Level-order BFS naturally aggregates per level.

        Algorithm (BFS):
        - Queue levels; track best sum and level index.

        Complexity: O(n) time, O(w) space for width w.
        """
        q: Deque = deque([root])
        best_sum = float("-inf")
        best_lvl = 1
        lvl = 0
        while q:
            lvl += 1
            s = 0
            for _ in range(len(q)):
                node = q.popleft()
                s += node.val
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
            if s > best_sum:
                best_sum = s
                best_lvl = lvl
        return best_lvl

    def maxLevelSum_dfs(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Classic DFS alternate: accumulate sums in a list/dict by depth, then
        find the best level.

        Algorithm:
        - dfs(node, depth); sums[depth]+=val; argmax with smallest depth.

        Complexity: O(n) time, O(h) space.
        """
        sums: List[int] = []

        def dfs(node: Optional[TreeNode], d: int) -> None:
            if not node:
                return
            if d == len(sums):
                sums.append(0)
            sums[d] += node.val
            dfs(node.left, d + 1)
            dfs(node.right, d + 1)

        dfs(root, 0)
        best = max(sums)
        return sums.index(best) + 1
# @lc code=end
