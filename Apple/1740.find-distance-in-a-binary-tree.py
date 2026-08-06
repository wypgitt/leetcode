#
# @lc app=leetcode id=1740 lang=python3
#
# [1740] Find Distance in a Binary Tree
#
# https://leetcode.com/problems/find-distance-in-a-binary-tree/description/
#
# algorithms
# Medium (74.43%)
# Likes:    487
# Dislikes: 19
# Total Accepted:    36.2K
# Total Submissions: 48.6K
# Testcase Example:  "[3,5,1,6,2,0,8,null,null,7,4]\n5\n0"
#
#
# Given the root of a binary tree and two integers p and q, return the
# distance between the nodes of value p and value q in the tree.
#
# The distance between two nodes is the number of edges on the path from
# one to the other.
#
# Example 1:
#
# Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 0
# Output: 3
# Explanation: There are 3 edges between 5 and 0: 5-3-1-0.
#
# Example 2:
#
# Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 7
# Output: 2
# Explanation: There are 2 edges between 5 and 7: 5-2-7.
#
# Example 3:
#
# Input: root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 5
# Output: 0
# Explanation: The distance between a node and itself is 0.
#
# Constraints:
#
# The number of nodes in the tree is in the range [1, 10^4].
#
# 0 <= Node.val <= 10^9
#
# All Node.val are unique.
#
# p and q are values in the tree.
#
# @lc code=start
from typing import Optional
from collections import deque

# Definition for a binary tree node.
# class TreeNode:
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right


class Solution:
    def findDistance(self, root: Optional["TreeNode"], p: int, q: int) -> int:
        """
        Interview explanation:
        Premium. Distance between nodes p and q equals depth(p)+depth(q)-2*depth(LCA).

        Algorithm:
        - Find LCA; DFS distance from LCA to p and to q; sum.

        Complexity: O(n) time, O(h) space.
        """
        def lca(node):
            if not node or node.val in (p, q):
                return node
            L, R = lca(node.left), lca(node.right)
            if L and R:
                return node
            return L or R

        def dist(node, target, d):
            if not node:
                return -1
            if node.val == target:
                return d
            left = dist(node.left, target, d + 1)
            if left != -1:
                return left
            return dist(node.right, target, d + 1)

        anc = lca(root)
        return dist(anc, p, 0) + dist(anc, q, 0)

    def findDistance_bfs(self, root: Optional["TreeNode"], p: int, q: int) -> int:
        """
        Interview explanation:
        Alternate: parent pointers + BFS from p to q on the undirected tree.

        Algorithm:
        - DFS build parent map; BFS from p until q.

        Complexity: O(n) time, O(n) space.
        """
        parent = {}
        nodes = {}

        def dfs(node, par):
            if not node:
                return
            parent[node] = par
            nodes[node.val] = node
            dfs(node.left, node)
            dfs(node.right, node)

        dfs(root, None)
        start = nodes[p]
        dq = deque([(start, 0)])
        seen = {start}
        while dq:
            cur, d = dq.popleft()
            if cur.val == q:
                return d
            for nei in (cur.left, cur.right, parent[cur]):
                if nei and nei not in seen:
                    seen.add(nei)
                    dq.append((nei, d + 1))
        return -1
# @lc code=end
