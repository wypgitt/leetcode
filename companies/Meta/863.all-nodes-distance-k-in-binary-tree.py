#
# @lc app=leetcode id=863 lang=python3
#
# [863] All Nodes Distance K in Binary Tree
#
# https://leetcode.com/problems/all-nodes-distance-k-in-binary-tree/description/
#
# algorithms
# Medium (67.96%)
# Likes:    12258
# Dislikes: 279
# Total Accepted:    727K
# Total Submissions: 1.1M
# Testcase Example:  "[3,5,1,6,2,0,8,null,null,7,4]"
#
# Given the root of a binary tree, the value of a target node target, and an
# integer k, return an array of the values of all nodes that have a distance k
# from the target node.
#
# You can return the answer in any order.
#
# Example 1:
#
# Input: root = [3,5,1,6,2,0,8,null,null,7,4], target = 5, k = 2
# Output: [7,4,1]
# Explanation: The nodes that are a distance 2 from the target node (with value
# 5) have values 7, 4, and 1.
#
# Example 2:
#
# Input: root = [1], target = 1, k = 3
# Output: []
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 500].
#
# 0 <= Node.val <= 500
#
# All the values Node.val are unique.
#
# target is the value of one of the nodes in the tree.
#
# 0 <= k <= 1000
#

# @lc code=start
from collections import deque
from typing import List

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, x):
#         self.val = x
#         self.left = None
#         self.right = None


class Solution:
    def distanceK(self, root: TreeNode, target: TreeNode, k: int) -> List[int]:
        """
        Interview explanation:
        Tree edges are downward-only; add parent links so the tree is an
        undirected graph, then BFS from target for exactly k steps.

        Algorithm (parent map + BFS):
        - DFS/BFS build parent[child]=parent.
        - BFS from target; track visited; collect nodes at distance k.

        Complexity: O(n) time, O(n) space.
        """
        parent = {}

        def build(node: TreeNode, p: TreeNode) -> None:
            if not node:
                return
            parent[node] = p
            build(node.left, node)
            build(node.right, node)

        build(root, None)
        q = deque([(target, 0)])
        seen = {target}
        ans: List[int] = []
        while q:
            node, d = q.popleft()
            if d == k:
                ans.append(node.val)
                continue
            for nei in (node.left, node.right, parent[node]):
                if nei and nei not in seen:
                    seen.add(nei)
                    q.append((nei, d + 1))
        return ans

    def distanceK_dfs(self, root: TreeNode, target: TreeNode, k: int) -> List[int]:
        """
        Interview explanation:
        Alternate: same parent map, then DFS from target counting remaining
        distance; collect when rem==0.

        Algorithm:
        - Build parents; dfs(node, rem): if rem==0 record; recurse unvisited neighbors.

        Complexity: O(n) time, O(n) space.
        """
        parent = {}

        def build(node: TreeNode, p: TreeNode) -> None:
            if not node:
                return
            parent[node] = p
            build(node.left, node)
            build(node.right, node)

        build(root, None)
        ans: List[int] = []
        seen = set()

        def dfs(node: TreeNode, rem: int) -> None:
            if not node or node in seen:
                return
            seen.add(node)
            if rem == 0:
                ans.append(node.val)
                return
            for nei in (node.left, node.right, parent[node]):
                dfs(nei, rem - 1)

        dfs(target, k)
        return ans
# @lc code=end

