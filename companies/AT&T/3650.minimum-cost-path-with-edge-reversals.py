#
# @lc app=leetcode id=3650 lang=python3
#
# [3650] Minimum Cost Path with Edge Reversals
#
# https://leetcode.com/problems/minimum-cost-path-with-edge-reversals/description/
#
# algorithms
# Medium (61.76%)
# Likes:    470
# Dislikes: 25
# Total Accepted:    107K
# Total Submissions: 173.2K
# Testcase Example:  "4\n[[0,1,3],[3,1,1],[2,3,4],[0,2,2]]"
#
#
# You are given a directed, weighted graph with n nodes labeled from 0 to
# n - 1, and an array edges where edges[i] = [u_i, v_i, w_i] represents a
# directed edge from node u_i to node v_i with cost w_i.
#
# Each node u_i has a switch that can be used at most once: when you
# arrive at u_i and have not yet used its switch, you may activate it on
# one of its incoming edges v_i → u_i reverse that edge to u_i → v_i and
# immediately traverse it.
#
# The reversal is only valid for that single move, and using a reversed
# edge costs 2 * w_i.
#
# Return the minimum total cost to travel from node 0 to node n - 1. If it
# is not possible, return -1.
#
# Example 1:
#
# Input: n = 4, edges = [[0,1,3],[3,1,1],[2,3,4],[0,2,2]]
#
# Output: 5
#
# Explanation:
#
# Use the path 0 → 1 (cost 3).
#
# At node 1 reverse the original edge 3 → 1 into 1 → 3 and traverse it at
# cost 2 * 1 = 2.
#
# Total cost is 3 + 2 = 5.
#
# Example 2:
#
# Input: n = 4, edges = [[0,2,1],[2,1,1],[1,3,1],[2,3,3]]
#
# Output: 3
#
# Explanation:
#
# No reversal is needed. Take the path 0 → 2 (cost 1), then 2 → 1 (cost
# 1), then 1 → 3 (cost 1).
#
# Total cost is 1 + 1 + 1 = 3.
#
# Constraints:
#
# 2 <= n <= 5 * 10^4
#
# 1 <= edges.length <= 10^5
#
# edges[i] = [u_i, v_i, w_i]
#
# 0 <= u_i, v_i <= n - 1
#
# 1 <= w_i <= 1000
#

# @lc code=start
from typing import List
import heapq


class Solution:
    def minCost(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Reversing an incoming edge costs 2w — model as an extra reverse arc
        and run Dijkstra from 0 to n-1.

        Algorithm:
        - For each u→v (w), add u→v cost w and v→u cost 2w; Dijkstra.

        Complexity: O((n+m) log n) time, O(n+m) space.
        """
        graph = [[] for _ in range(n)]
        for u, v, w in edges:
            graph[u].append((v, w))
            graph[v].append((u, 2 * w))
        dist = [float("inf")] * n
        dist[0] = 0
        pq = [(0, 0)]
        while pq:
            d, u = heapq.heappop(pq)
            if d > dist[u]:
                continue
            if u == n - 1:
                return d
            for v, w in graph[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(pq, (nd, v))
        return -1
# @lc code=end

