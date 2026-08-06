#
# @lc app=leetcode id=515 lang=python3
#
# [515] Find Largest Value in Each Tree Row
#
# https://leetcode.com/problems/find-largest-value-in-each-tree-row/description/
#
# algorithms
# Medium (66.37%)
# Likes:    4160
# Dislikes: 130
# Total Accepted:    534K
# Total Submissions: 804K
# Testcase Example:  "[1,3,2,5,3,null,9]"
#
# Given the root of a binary tree, return an array of the largest value in each
# row of the tree (0-indexed).
#
# Example 1:
#
# Input: root = [1,3,2,5,3,null,9]
# Output: [1,3,9]
#
# Example 2:
#
# Input: root = [1,2,3]
# Output: [1,3]
#
# Constraints:
#
# The number of nodes in the tree will be in the range [0, 10^4].
#
# -2^31 <= Node.val <= 2^31 - 1
#

# @lc code=start
from collections import deque
from typing import List, Optional
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def largestValues(self, root: Optional[TreeNode]) -> List[int]:
        """
        Interview explanation:
        Level-order BFS: for each level, track the maximum node value.

        Algorithm:
        - Process queue level by level; append max of the level to the answer.

        Complexity: O(n) time, O(w) queue space.
        """
        if not root:
            return []
        ans: List[int] = []
        queue = deque([root])
        while queue:
            level_max = float("-inf")
            for _ in range(len(queue)):
                node = queue.popleft()
                level_max = max(level_max, node.val)
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
            ans.append(level_max)
        return ans

    def largestValues_dfs(self, root: Optional[TreeNode]) -> List[int]:
        """
        Interview explanation:
        Alternate DFS: maintain ans[depth] = max value seen at that depth.

        Algorithm:
        - Preorder/DFS with depth; update ans[depth] when visiting a node.

        Complexity: O(n) time, O(h) recursion space (+ O(h) answer).
        """
        ans: List[int] = []

        def dfs(node: Optional[TreeNode], depth: int) -> None:
            if not node:
                return
            if depth == len(ans):
                ans.append(node.val)
            else:
                ans[depth] = max(ans[depth], node.val)
            dfs(node.left, depth + 1)
            dfs(node.right, depth + 1)

        dfs(root, 0)
        return ans
# @lc code=end
