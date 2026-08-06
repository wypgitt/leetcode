#
# @lc app=leetcode id=882 lang=python3
#
# [882] Reachable Nodes In Subdivided Graph
#
# https://leetcode.com/problems/reachable-nodes-in-subdivided-graph/description/
#
# algorithms
# Hard (52.63%)
# Likes:    915
# Dislikes: 230
# Total Accepted:    39.6K
# Total Submissions: 75.2K
# Testcase Example:  "[[0,1,10],[0,2,1],[1,2,2]]"
#
# You are given an undirected graph (the "original graph") with n nodes labeled
# from 0 to n - 1. You decide to subdivide each edge in the graph into a chain
# of nodes, with the number of new nodes varying between each edge.
#
# The graph is given as a 2D array of edges where edges[i] = [u_i, v_i, cnt_i]
# indicates that there is an edge between nodes u_i and v_i in the original
# graph, and cnt_i is the total number of new nodes that you will subdivide the
# edge into. Note that cnt_i == 0 means you will not subdivide the edge.
#
# To subdivide the edge [u_i, v_i], replace it with (cnt_i + 1) new edges and
# cnt_i new nodes. The new nodes are x_1, x_2, ..., x_cnt_i, and the new edges
# are [u_i, x_1], [x_1, x_2], [x_2, x_3], ..., [x_cnt_i-1, x_cnt_i], [x_cnt_i,
# v_i].
#
# In this new graph, you want to know how many nodes are reachable from the
# node 0, where a node is reachable if the distance is maxMoves or less.
#
# Given the original graph and maxMoves, return the number of nodes that are
# reachable from node 0 in the new graph.
#
# Example 1:
#
# Input: edges = [[0,1,10],[0,2,1],[1,2,2]], maxMoves = 6, n = 3
# Output: 13
# Explanation: The edge subdivisions are shown in the image above.
# The nodes that are reachable are highlighted in yellow.
#
# Example 2:
#
# Input: edges = [[0,1,4],[1,2,6],[0,2,8],[1,3,1]], maxMoves = 10, n = 4
# Output: 23
#
# Example 3:
#
# Input: edges = [[1,2,4],[1,4,5],[1,3,1],[2,3,4],[3,4,5]], maxMoves = 17, n =
# 5
# Output: 1
# Explanation: Node 0 is disconnected from the rest of the graph, so only node
# 0 is reachable.
#
# Constraints:
#
# 0 <= edges.length <= min(n * (n - 1) / 2, 10^4)
#
# edges[i].length == 3
#
# 0 <= u_i < v_i < n
#
# There are no multiple edges in the graph.
#
# 0 <= cnt_i <= 10^4
#
# 0 <= maxMoves <= 10^9
#
# 1 <= n <= 3000
#

# @lc code=start
import heapq
from typing import Dict, List, Tuple


class Solution:
    def reachableNodes(self, edges: List[List[int]], maxMoves: int, n: int) -> int:
        """
        Interview explanation:
        Each edge u-v with cnt new nodes. Dijkstra from 0 for min moves to
        original nodes; then for each edge count how many subdivided nodes
        are reachable from either end within remaining moves.

        Algorithm:
        - Graph undirected weighted by cnt+1.
        - Dijkstra dist[u]; ans = #original nodes with dist<=maxMoves.
        - For edge (u,v,cnt): ans += min(cnt, max(0,maxMoves-dist[u]) +
          max(0,maxMoves-dist[v])).

        Complexity: O((n+E) log n) time, O(n+E) space.
        """
        graph: List[List[Tuple[int, int]]] = [[] for _ in range(n)]
        for u, v, cnt in edges:
            graph[u].append((v, cnt))
            graph[v].append((u, cnt))
        dist = [float("inf")] * n
        dist[0] = 0
        pq = [(0, 0)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            for v, cnt in graph[u]:
                nd = d + cnt + 1
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        ans = sum(1 for d in dist if d <= maxMoves)
        for u, v, cnt in edges:
            a = max(0, maxMoves - dist[u]) if dist[u] != float("inf") else 0
            b = max(0, maxMoves - dist[v]) if dist[v] != float("inf") else 0
            ans += min(cnt, a + b)
        return ans
# @lc code=end

