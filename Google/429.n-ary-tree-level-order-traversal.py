#
# @lc app=leetcode id=429 lang=python3
#
# [429] N-ary Tree Level Order Traversal
#
# https://leetcode.com/problems/n-ary-tree-level-order-traversal/description/
#
# algorithms
# Medium (71.62%)
# Likes:    3769
# Dislikes: 147
# Total Accepted:    374K
# Total Submissions: 523K
# Testcase Example:  "[1,null,3,2,4,null,5,6]"
#
# Given an n-ary tree, return the level order traversal of its nodes' values.
#
# Nary-Tree input serialization is represented in their level order traversal,
# each group of children is separated by the null value (See examples).
#
# Example 1:
#
# Input: root = [1,null,3,2,4,null,5,6]
# Output: [[1],[3,2,4],[5,6]]
#
# Example 2:
#
# Input: root =
# [1,null,2,3,4,5,null,null,6,7,null,8,null,9,10,null,null,11,null,12,null,13,null,null,14]
# Output: [[1],[2,3,4,5],[6,7,8,9,10],[11,12,13],[14]]
#
# Constraints:
#
# The height of the n-ary tree is less than or equal to 1000
#
# The total number of nodes is between [0, 10^4]
#

# @lc code=start

from collections import deque
from typing import List, Optional

"""
# Definition for a Node.
class Node:
    def __init__(self, val: Optional[int] = None, children: Optional[List['Node']] = None):
        self.val = val
        self.children = children
"""


class Solution:
    def levelOrder(self, root: "Node") -> List[List[int]]:
        """
        Interview explanation:
        Classic BFS level-order on an N-ary tree: process each level's nodes,
        collect values, enqueue all children for the next level.

        Algorithm:
        - Queue with root; while queue: size=len(q); gather level; enqueue kids.

        Complexity: O(n) time, O(n) space.
        """
        if not root:
            return []
        ans = []
        q = deque([root])
        while q:
            level = []
            for _ in range(len(q)):
                node = q.popleft()
                level.append(node.val)
                if node.children:
                    q.extend(node.children)
            ans.append(level)
        return ans

    def levelOrderDFS(self, root: "Node") -> List[List[int]]:
        """
        Interview explanation:
        Alternate DFS: pass depth; append val into ans[depth], recurse children.

        Algorithm:
        - dfs(node, d): ensure ans has slot d; append; recurse kids with d+1.

        Complexity: O(n) time, O(h) recursion space.
        """
        ans: List[List[int]] = []

        def dfs(node: "Node", d: int) -> None:
            if not node:
                return
            if d == len(ans):
                ans.append([])
            ans[d].append(node.val)
            if node.children:
                for ch in node.children:
                    dfs(ch, d + 1)

        dfs(root, 0)
        return ans
# @lc code=end
