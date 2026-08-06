#
# @lc app=leetcode id=3778 lang=python3
#
# [3778] Minimum Distance Excluding One Maximum Weighted Edge
#
# https://leetcode.com/problems/minimum-distance-excluding-one-maximum-weighted-edge/description/
#
# algorithms
# Medium (46.56%)
# Likes:    3
# Dislikes: 3
# Total Accepted:    359
# Total Submissions: 771
# Testcase Example:  "5\n[[0,1,2],[1,2,7],[2,3,7],[3,4,4]]"
#
#
# You are given a positive integer n and a 2D integer array edges, where
# edges[i] = [u_i, v_i, w_i].
#
# There is a weighted connected simple undirected graph with n nodes
# labeled from 0 to n - 1. Each [u_i, v_i, w_i] in edges represents an
# edge between node u_i and node v_i with positive weight w_i.
#
# The cost of a path is the sum of weights of the edges in the path,
# excluding the edge with the maximum weight. If there are multiple edges
# in the path with the maximum weight, only the first such edge is
# excluded.
#
# Return an integer representing the minimum cost of a path going from
# node 0 to node n - 1.
#
# Example 1:
#
# Input: n = 5, edges = [[0,1,2],[1,2,7],[2,3,7],[3,4,4]]
#
# Output: 13
#
# Explanation:
#
# There is only one path going from node 0 to node 4: 0 -> 1 -> 2 -> 3 ->
# 4.
#
# The edge weights on this path are 2, 7, 7, and 4.
#
# Excluding the first edge with maximum weight, which is 1 -> 2, the cost
# of this path is 2 + 7 + 4 = 13.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1,1],[1,2,1],[0,2,50000]]
#
# Output: 0
#
# Explanation:
#
# There are two paths going from node 0 to node 2:
#
# 0 -> 1 -> 2
#
# The edge weights on this path are 1 and 1.
#
# Excluding the first edge with maximum weight, which is 0 -> 1, the cost
# of this path is 1.
#
# 0 -> 2
#
# The only edge weight on this path is 1.
#
# Excluding the first edge with maximum weight, which is 0 -> 2, the cost
# of this path is 0.
#
# The minimum cost is min(1, 0) = 0.
#
# Constraints:
#
# 2 <= n <= 5 * 10^4
#
# n - 1 <= edges.length <= 10^9
#
# edges[i] = [u_i, v_i, w_i]
#
# 0 <= u_i < v_i < n
#
# [u_i, v_i] != [u_j, v_j]
#
# 1 <= w_i <= 5 * 10^4
#
# The graph is connected.
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def minCostExcludingMax(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Path cost is sum minus its heaviest edge, equivalent to shortest path
        where we may zero out exactly one edge weight.

        Algorithm:
        - Dijkstra on state (node, used_skip).
        - From used=0, either pay w or skip (go to used=1 paying 0).

        Complexity: O((n + m) log n) time, O(n + m) space.
        """
        adj: List[List[tuple]] = [[] for _ in range(n)]
        for u, v, w in edges:
            adj[u].append((v, w))
            adj[v].append((u, w))
        INF = 10**30
        dist = [[INF, INF] for _ in range(n)]
        dist[0][0] = 0
        pq = [(0, 0, 0)]  # cost, node, used
        while pq:
            cur, u, used = heapq.heappop(pq)
            if cur != dist[u][used]:
                continue
            if u == n - 1 and used == 1:
                return cur
            for v, w in adj[u]:
                nxt = cur + w
                if nxt < dist[v][used]:
                    dist[v][used] = nxt
                    heapq.heappush(pq, (nxt, v, used))
                if used == 0 and cur < dist[v][1]:
                    dist[v][1] = cur
                    heapq.heappush(pq, (cur, v, 1))
        return dist[n - 1][1]
# @lc code=end
