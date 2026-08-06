#
# @lc app=leetcode id=2203 lang=python3
#
# [2203] Minimum Weighted Subgraph With the Required Paths
#
# https://leetcode.com/problems/minimum-weighted-subgraph-with-the-required-paths/description/
#
# algorithms
# Hard (43.05%)
# Likes:    805
# Dislikes: 23
# Total Accepted:    24.7K
# Total Submissions: 57.4K
# Testcase Example:  "6\n[[0,2,2],[0,5,6],[1,0,3],[1,4,5],[2,1,1],[2,3,3],[2,3,4],[3,4,2],[4,5,1]]\n0\n1\n5"
#
# You are given an integer n denoting the number of nodes of a weighted directed
# graph. The nodes are numbered from 0 to n - 1.
#
# You are also given a 2D integer array edges where edges[i] = [from_i, to_i,
# weight_i] denotes that there exists a directed edge from from_i to to_i with
# weight weight_i.
#
# Lastly, you are given three distinct integers src1, src2, and dest denoting
# three distinct nodes of the graph.
#
# Return the minimum weight of a subgraph of the graph such that it is possible
# to reach dest from both src1 and src2 via a set of edges of this subgraph. In
# case such a subgraph does not exist, return -1.
#
# A subgraph is a graph whose vertices and edges are subsets of the original
# graph. The weight of a subgraph is the sum of weights of its constituent
# edges.
#
#
#
# Example 1:
#
# Input: n = 6, edges =
# [[0,2,2],[0,5,6],[1,0,3],[1,4,5],[2,1,1],[2,3,3],[2,3,4],[3,4,2],[4,5,1]],
# src1 = 0, src2 = 1, dest = 5
# Output: 9
# Explanation:
# The above figure represents the input graph.
# The blue edges represent one of the subgraphs that yield the optimal answer.
# Note that the subgraph [[1,0,3],[0,5,6]] also yields the optimal answer. It is
# not possible to get a subgraph with less weight satisfying all the
# constraints.
#
# Example 2:
#
# Input: n = 3, edges = [[0,1,1],[2,1,1]], src1 = 0, src2 = 1, dest = 2
# Output: -1
# Explanation:
# The above figure represents the input graph.
# It can be seen that there does not exist any path from node 1 to node 2, hence
# there are no subgraphs satisfying all the constraints.
#
#
#
# Constraints:
#
#
# 3 <= n <= 10^5
#
#
# 0 <= edges.length <= 10^5
#
#
# edges[i].length == 3
#
#
# 0 <= from_i, to_i, src1, src2, dest <= n - 1
#
#
# from_i != to_i
#
#
# src1, src2, and dest are pairwise distinct.
#
#
# 1 <= weight[i] <= 10^5
#

# @lc code=start
from typing import List
from collections import defaultdict
import heapq


class Solution:
    def minimumWeight(self, n: int, edges: List[List[int]], src1: int, src2: int, dest: int) -> int:
        """
        Interview explanation:
        Directed weighted graph. Min total edge weight of a subgraph where both
        src1 and src2 reach dest (shared edges counted once). Equivalent to some
        meeting node x: d(src1,x)+d(src2,x)+d(x,dest).

        Algorithm:
        - Dijkstra from src1, src2 on G; from dest on reverse G; min over x.

        Complexity: O((n+m) log n) time, O(n+m) space.
        """
        g = defaultdict(list)
        rg = defaultdict(list)
        for u, v, w in edges:
            g[u].append((v, w))
            rg[v].append((u, w))

        def dijkstra(graph, start: int) -> List[float]:
            dist = [float("inf")] * n
            dist[start] = 0
            pq = [(0, start)]
            while pq:
                d, u = heapq.heappop(pq)
                if d > dist[u]:
                    continue
                for v, w in graph[u]:
                    nd = d + w
                    if nd < dist[v]:
                        dist[v] = nd
                        heapq.heappush(pq, (nd, v))
            return dist

        d1, d2, dd = dijkstra(g, src1), dijkstra(g, src2), dijkstra(rg, dest)
        ans = float("inf")
        for x in range(n):
            if d1[x] < float("inf") and d2[x] < float("inf") and dd[x] < float("inf"):
                ans = min(ans, d1[x] + d2[x] + dd[x])
        return -1 if ans == float("inf") else int(ans)
# @lc code=end
