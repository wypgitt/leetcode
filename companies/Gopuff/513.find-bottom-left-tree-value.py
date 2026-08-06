#
# @lc app=leetcode id=513 lang=python3
#
# [513] Find Bottom Left Tree Value
#
# https://leetcode.com/problems/find-bottom-left-tree-value/description/
#
# algorithms
# Medium (72.5%)
# Likes:    4040
# Dislikes: 303
# Total Accepted:    457K
# Total Submissions: 631K
# Testcase Example:  "[2,1,3]"
#
# Given the root of a binary tree, return the leftmost value in the last row of
# the tree.
#
# Example 1:
#
# Input: root = [2,1,3]
# Output: 1
#
# Example 2:
#
# Input: root = [1,2,3,4,null,5,6,null,null,7]
# Output: 7
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# -2^31 <= Node.val <= 2^31 - 1
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
    def findBottomLeftValue(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Level-order BFS: the first node dequeued on each level is the leftmost.
        After the last level, that value is the bottom-left.

        Algorithm:
        - Queue BFS left-to-right.
        - At each level, record the first node's value.
        - Return the last recorded leftmost value.

        Complexity: O(n) time, O(w) queue space.
        """
        queue = deque([root])
        leftmost = root.val
        while queue:
            leftmost = queue[0].val
            for _ in range(len(queue)):
                node = queue.popleft()
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)
        return leftmost

    def findBottomLeftValue_dfs(self, root: Optional[TreeNode]) -> int:
        """
        Interview explanation:
        Alternate: DFS tracking (depth, value). Prefer deeper nodes; at the
        same depth, the first visit (left-first) is leftmost.

        Algorithm:
        - Recurse left then right; update answer when depth increases.

        Complexity: O(n) time, O(h) recursion space.
        """
        self.ans = root.val
        self.max_depth = 0

        def dfs(node: Optional[TreeNode], depth: int) -> None:
            if not node:
                return
            if depth > self.max_depth:
                self.max_depth = depth
                self.ans = node.val
            dfs(node.left, depth + 1)
            dfs(node.right, depth + 1)

        dfs(root, 0)
        return self.ans
# @lc code=end
