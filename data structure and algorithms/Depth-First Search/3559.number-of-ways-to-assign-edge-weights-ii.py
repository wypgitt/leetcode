#
# @lc app=leetcode id=3559 lang=python3
#
# [3559] Number of Ways to Assign Edge Weights II
#
# https://leetcode.com/problems/number-of-ways-to-assign-edge-weights-ii/description/
#
# algorithms
# Hard (71.95%)
# Likes:    276
# Dislikes: 14
# Total Accepted:    68.8K
# Total Submissions: 95.7K
# Testcase Example:  "[[1,2]]\n[[1,1],[1,2]]"
#
#
# There is an undirected tree with n nodes labeled from 1 to n, rooted at
# node 1. The tree is represented by a 2D integer array edges of length n
# - 1, where edges[i] = [u_i, v_i] indicates that there is an edge between
# nodes u_i and v_i.
#
# Initially, all edges have a weight of 0. You must assign each edge a
# weight of either 1 or 2.
#
# The cost of a path between any two nodes u and v is the total weight of
# all edges in the path connecting them.
#
# You are given a 2D integer array queries. For each queries[i] = [u_i,
# v_i], determine the number of ways to assign weights to edges in the
# path such that the cost of the path between u_i and v_i is odd.
#
# Return an array answer, where answer[i] is the number of valid
# assignments for queries[i].
#
# Since the answer may be large, apply modulo 10^9 + 7 to each answer[i].
#
# Note: For each query, disregard all edges not in the path between node
# u_i and v_i.
#
# Example 1:
#
# Input: edges = [[1,2]], queries = [[1,1],[1,2]]
#
# Output: [0,1]
#
# Explanation:
#
# Query [1,1]: The path from Node 1 to itself consists of no edges, so the
# cost is 0. Thus, the number of valid assignments is 0.
#
# Query [1,2]: The path from Node 1 to Node 2 consists of one edge (1 →
# 2). Assigning weight 1 makes the cost odd, while 2 makes it even. Thus,
# the number of valid assignments is 1.
#
# Example 2:
#
# Input: edges = [[1,2],[1,3],[3,4],[3,5]], queries = [[1,4],[3,4],[2,5]]
#
# Output: [2,1,4]
#
# Explanation:
#
# Query [1,4]: The path from Node 1 to Node 4 consists of two edges (1 → 3
# and 3 → 4). Assigning weights (1,2) or (2,1) results in an odd cost.
# Thus, the number of valid assignments is 2.
#
# Query [3,4]: The path from Node 3 to Node 4 consists of one edge (3 →
# 4). Assigning weight 1 makes the cost odd, while 2 makes it even. Thus,
# the number of valid assignments is 1.
#
# Query [2,5]: The path from Node 2 to Node 5 consists of three edges (2 →
# 1, 1 → 3, and 3 → 5). Assigning (1,2,2), (2,1,2), (2,2,1), or (1,1,1)
# makes the cost odd. Thus, the number of valid assignments is 4.
#
# Constraints:
#
# 2 <= n <= 10^5
#
# edges.length == n - 1
#
# edges[i] == [u_i, v_i]
#
# 1 <= queries.length <= 10^5
#
# queries[i] == [u_i, v_i]
#
# 1 <= u_i, v_i <= n
#
# edges represents a valid tree.
#

# @lc code=start
from typing import List


class Solution:
    def assignEdgeWeights(self, edges: List[List[int]], queries: List[List[int]]) -> List[int]:
        """
        Interview explanation:
        For a path of d edges with weights in {1,2}, odd path sums occur in
        2^{d-1} ways (d ≥ 1), else 0. Answer each query with that formula using
        tree distance.

        Algorithm:
        - Root at 1; binary lifting for LCA and depths.
        - d(u,v) = depth[u] + depth[v] - 2 * depth[lca(u,v)].
        - answer = 0 if d == 0 else 2^{d-1} mod 1e9+7.

        Complexity: O((n + q) log n) time, O(n log n) space.
        """
        MOD = 10**9 + 7
        n = len(edges) + 1
        g = [[] for _ in range(n + 1)]
        for u, v in edges:
            g[u].append(v)
            g[v].append(u)

        LOG = (n + 1).bit_length()
        up = [[0] * (n + 1) for _ in range(LOG)]
        depth = [0] * (n + 1)

        stack = [(1, 0)]
        while stack:
            u, p = stack.pop()
            up[0][u] = p
            for v in g[u]:
                if v == p:
                    continue
                depth[v] = depth[u] + 1
                stack.append((v, u))

        for k in range(1, LOG):
            for v in range(1, n + 1):
                up[k][v] = up[k - 1][up[k - 1][v]]

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

        ans = []
        for u, v in queries:
            d = depth[u] + depth[v] - 2 * depth[lca(u, v)]
            ans.append(0 if d == 0 else pow(2, d - 1, MOD))
        return ans
# @lc code=end
