#
# @lc app=leetcode id=3604 lang=python3
#
# [3604] Minimum Time to Reach Destination in Directed Graph
#
# https://leetcode.com/problems/minimum-time-to-reach-destination-in-directed-graph/description/
#
# algorithms
# Medium (45.56%)
# Likes:    112
# Dislikes: 4
# Total Accepted:    19K
# Total Submissions: 41.6K
# Testcase Example:  "3\n[[0,1,0,1],[1,2,2,5]]"
#
#
# You are given an integer n and a directed graph with n nodes labeled
# from 0 to n - 1. This is represented by a 2D array edges, where edges[i]
# = [u_i, v_i, start_i, end_i] indicates an edge from node u_i to v_i that
# can only be used at any integer time t such that start_i <= t <= end_i.
#
# You start at node 0 at time 0.
#
# In one unit of time, you can either:
#
# Wait at your current node without moving, or
#
# Travel along an outgoing edge from your current node if the current time
# t satisfies start_i <= t <= end_i.
#
# Return the minimum time required to reach node n - 1. If it is
# impossible, return -1.
#
# Example 1:
#
# Input: n = 3, edges = [[0,1,0,1],[1,2,2,5]]
#
# Output: 3
#
# Explanation:
#
# The optimal path is:
#
# At time t = 0, take the edge (0 → 1) which is available from 0 to 1. You
# arrive at node 1 at time t = 1, then wait until t = 2.
#
# At time t = 2, take the edge (1 → 2) which is available from 2 to 5. You
# arrive at node 2 at time 3.
#
# Hence, the minimum time to reach node 2 is 3.
#
# Example 2:
#
# Input: n = 4, edges = [[0,1,0,3],[1,3,7,8],[0,2,1,5],[2,3,4,7]]
#
# Output: 5
#
# Explanation:
#
# The optimal path is:
#
# Wait at node 0 until time t = 1, then take the edge (0 → 2) which is
# available from 1 to 5. You arrive at node 2 at t = 2.
#
# Wait at node 2 until time t = 4, then take the edge (2 → 3) which is
# available from 4 to 7. You arrive at node 3 at t = 5.
#
# Hence, the minimum time to reach node 3 is 5.
#
# Example 3:
#
# Input: n = 3, edges = [[1,0,1,3],[1,2,3,5]]
#
# Output: -1
#
# Explanation:
#
# Since there is no outgoing edge from node 0, it is impossible to reach
# node 2. Hence, the output is -1.
#
# Constraints:
#
# 1 <= n <= 10^5
#
# 0 <= edges.length <= 10^5
#
# edges[i] == [u_i, v_i, start_i, end_i]
#
# 0 <= u_i, v_i <= n - 1
#
# u_i != v_i
#
# 0 <= start_i <= end_i <= 10^9
#

# @lc code=start

import heapq
from typing import List


class Solution:
    def minTime(self, n: int, edges: List[List[int]]) -> int:
        """
        Interview explanation:
        Reach n-1 ASAP; each edge u→v is usable only while start≤t≤end.
        Waiting is free, so depart at max(arrival, start) if ≤ end.

        Algorithm:
        - Dijkstra on earliest arrival time per node.
        - For edge (v,s,e) from u at time t: if t≤e, arrive at max(t,s)+1.

        Complexity: O((n+E) log n) time, O(n+E) space.
        """
        adj: List[List[tuple]] = [[] for _ in range(n)]
        for u, v, s, e in edges:
            adj[u].append((v, s, e))

        best = [float("inf")] * n
        best[0] = 0
        heap = [(0, 0)]
        while heap:
            t, u = heapq.heappop(heap)
            if t != best[u]:
                continue
            if u == n - 1:
                return t
            for v, s, e in adj[u]:
                if t > e:
                    continue
                nt = max(t, s) + 1
                if nt < best[v]:
                    best[v] = nt
                    heapq.heappush(heap, (nt, v))
        return -1
# @lc code=end
