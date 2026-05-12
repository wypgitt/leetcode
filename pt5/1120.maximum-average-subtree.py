from __future__ import annotations

from typing import Optional, Tuple


# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def maximumAverageSubtree(self, root: Optional[TreeNode]) -> float:
        best = 0.0

        def dfs(node: Optional[TreeNode]) -> Tuple[int, int]:
            nonlocal best
            if node is None:
                return 0, 0

            left_sum, left_count = dfs(node.left)
            right_sum, right_count = dfs(node.right)
            total_sum = left_sum + right_sum + node.val
            total_count = left_count + right_count + 1
            best = max(best, total_sum / total_count)
            return total_sum, total_count

        dfs(root)
        return best

