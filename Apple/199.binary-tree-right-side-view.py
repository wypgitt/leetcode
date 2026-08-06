"""
Approach: Level-order traversal and record the last node of each level.
Data structure: a queue processes the tree level by level.
Interview logic: from the right side, the visible node at each depth is the rightmost node in that level's BFS order.
Complexity: O(n) time, O(w) space where w is maximum tree width.
Tests and edge cases: empty tree returns []; missing right children can still expose left nodes; skewed trees return all nodes.
"""
from __future__ import annotations
from collections import deque
from typing import List, Optional

# @lc code=start
from collections import deque
# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right
class Solution:
    def rightSideView(self, root: Optional[TreeNode]) -> List[int]:
        if not root:
            return []
        ans = []
        q = deque([root])
        while q:
            level_size = len(q)
            for i in range(level_size):
                node = q.popleft()
                if i == level_size - 1:
                    ans.append(node.val)
                if node.left:
                    q.append(node.left)
                if node.right:
                    q.append(node.right)
        return ans
# @lc code=end
