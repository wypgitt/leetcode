#
# @lc app=leetcode id=1302 lang=python3
#
# [1302] Deepest Leaves Sum
#
# https://leetcode.com/problems/deepest-leaves-sum/description/
#
# algorithms
# Medium (86.58%)
# Likes:    4864
# Dislikes: 127
# Total Accepted:    415K
# Total Submissions: 479K
# Testcase Example:  "[1,2,3,4,5,null,6,7,null,null,null,null,8]"
#
# Given the root of a binary tree, return the sum of values of its deepest
# leaves.
#
# Example 1:
#
# Input: root = [1,2,3,4,5,null,6,7,null,null,null,null,8]
# Output: 15
#
# Example 2:
#
# Input: root = [6,7,8,2,7,1,3,9,null,1,4,null,null,null,5]
# Output: 19
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# 1 <= Node.val <= 100
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


class Solution:
    def deepestLeavesSum(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Sum values of leaves at maximum depth. BFS level-order: the last level's
        sum is the answer.

        Algorithm (BFS):
        - Process levels; keep sum of current level; return final level sum.

        Complexity: O(n) time, O(w) space.
        """
        q = deque([root])
        while q:
            level_sum = 0
            for _ in range(len(q)):
                node = q.popleft()
                level_sum += node.val
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
        return level_sum

    def deepestLeavesSum_dfs(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Alternate DFS: track max depth; when deeper reset sum; when equal add.

        Algorithm:
        - dfs(node, d): update max_d/ans; recurse children.

        Complexity: O(n) time, O(h) space.
        """
        ans = 0
        max_d = -1

        def dfs(node: Optional[TreeNode], d: int) -> None:
            nonlocal ans, max_d
            if not node:
                return
            if d > max_d:
                max_d = d
                ans = node.val
            elif d == max_d:
                ans += node.val
            dfs(node.left, d + 1)
            dfs(node.right, d + 1)

        dfs(root, 0)
        return ans
# @lc code=end

