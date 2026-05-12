from __future__ import annotations

from collections import deque
from typing import Deque, Optional


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def maxLevelSum(self, root: Optional[TreeNode]) -> int:
        queue: Deque[TreeNode] = deque([root])
        best_sum = float("-inf")
        best_level = 1
        level = 1

        while queue:
            level_sum = 0
            for _ in range(len(queue)):
                node = queue.popleft()
                level_sum += node.val
                if node.left:
                    queue.append(node.left)
                if node.right:
                    queue.append(node.right)

            if level_sum > best_sum:
                best_sum = level_sum
                best_level = level
            level += 1

        return best_level

