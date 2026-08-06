#
# @lc app=leetcode id=3553 lang=python3
#
# [3553] Minimum Weighted Subgraph With the Required Paths II
#
# https://leetcode.com/problems/minimum-weighted-subgraph-with-the-required-paths-ii/description/
#
# algorithms
# Hard (50.81%)
# Likes:    56
# Dislikes: 4
# Total Accepted:    4.9K
# Total Submissions: 9.7K
# Testcase Example:  "[[0,1,2],[1,2,3],[1,3,5],[1,4,4],[2,5,6]]\n[[2,3,4],[0,2,5]]"
#
#
# You are given an undirected weighted tree with n nodes, numbered from 0
# to n - 1. It is represented by a 2D integer array edges of length n - 1,
# where edges[i] = [u_i, v_i, w_i] indicates that there is an edge between
# nodes u_i and v_i with weight w_i.​
#
# Additionally, you are given a 2D integer array queries, where queries[j]
# = [src1_j, src2_j, dest_j].
#
# Return an array answer of length equal to queries.length, where
# answer[j] is the minimum total weight of a subtree such that it is
# possible to reach dest_j from both src1_j and src2_j using edges in this
# subtree.
#
# A subtree here is any connected subset of nodes and edges of the
# original tree forming a valid tree.
#
# Example 1:
#
# Input: edges = [[0,1,2],[1,2,3],[1,3,5],[1,4,4],[2,5,6]], queries =
# [[2,3,4],[0,2,5]]
#
# Output: [12,11]
#
# Explanation:
#
# The blue edges represent one of the subtrees that yield the optimal
# answer.
#
# answer[0]: The total weight of the selected subtree that ensures a path
# from src1 = 2 and src2 = 3 to dest = 4 is 3 + 5 + 4 = 12.
#
# answer[1]: The total weight of the selected subtree that ensures a path
# from src1 = 0 and src2 = 2 to dest = 5 is 2 + 3 + 6 = 11.
#
# Example 2:
#
# Input: edges = [[1,0,8],[0,2,7]], queries = [[0,1,2]]
#
# Output: [15]
#
# Explanation:
#
# answer[0]: The total weight of the selected subtree that ensures a path
# from src1 = 0 and src2 = 1 to dest = 2 is 8 + 7 = 15.
#
# Constraints:
#
# 3 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[i].length == 3
#
# 0 <= u_i, v_i < n
#
# 1 <= w_i <= 10^4
#
# 1 <= queries.length <= 10^5
#
# queries[j].length == 3
#
# 0 <= src1_j, src2_j, dest_j < n
#
# src1_j, src2_j, and dest_j are pairwise distinct.
#
# The input is generated such that edges represents a valid tree.
#

# @lc code=start
from typing import List


class Solution:
    def minimumWeight(self, edges: List[List[int]], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        On a tree, the min-weight Steiner tree for three terminals a,b,c has
        weight (d(a,b) + d(b,c) + d(c,a)) / 2 — the three pairwise paths meet
        at their unique median.

        Algorithm:
        - Build the tree; binary-lift parents and weighted depth from root 0.
        - d(u,v) = depth[u] + depth[v] - 2 * depth[lca(u,v)].
        - Answer each query with the three-distance formula.

        Complexity: O((n + q) log n) time, O(n log n) space.
        """
        n = len(edges) + 1
        g = [[] for _ in range(n)]
        for u, v, w in edges:
            g[u].append((v, w))
            g[v].append((u, w))

        LOG = n.bit_length()
        up = [[-1] * n for _ in range(LOG)]
        depth = [0] * n
        dist = [0] * n

        stack = [0]
        parent = [-1] * n
        while stack:
            u = stack.pop()
            for v, w in g[u]:
                if v == parent[u]:
                    continue
                parent[v] = u
                up[0][v] = u
                depth[v] = depth[u] + 1
                dist[v] = dist[u] + w
                stack.append(v)

        for k in range(1, LOG):
            for v in range(n):
                p = up[k - 1][v]
                up[k][v] = up[k - 1][p] if p != -1 else -1

        def lca(a: int, b: int) -> int:
            if depth[a] < depth[b]:
                a, b = b, a
            diff = depth[a] - depth[b]
            bit = 0
            while diff:
                if diff & 1:
                    a = up[bit][a]
                diff >>= 1
                bit += 1
            if a == b:
                return a
            for k in range(LOG - 1, -1, -1):
                if up[k][a] != up[k][b]:
                    a = up[k][a]
                    b = up[k][b]
            return up[0][a]

        def path(a: int, b: int) -> int:
            return dist[a] + dist[b] - 2 * dist[lca(a, b)]

        ans = []
        for a, b, c in queries:
            ans.append((path(a, b) + path(b, c) + path(c, a)) // 2)
        return ans
# @lc code=end
