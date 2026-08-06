#
# @lc app=leetcode id=787 lang=python3
#
# [787] Cheapest Flights Within K Stops
#
# https://leetcode.com/problems/cheapest-flights-within-k-stops/description/
#
# algorithms
# Medium (42.35%)
# Likes:    11416
# Dislikes: 474
# Total Accepted:    983K
# Total Submissions: 2.3M
# Testcase Example:  "4"
#
# There are n cities connected by some number of flights. You are given an
# array flights where flights[i] = [from_i, to_i, price_i] indicates that there
# is a flight from city from_i to city to_i with cost price_i.
#
# You are also given three integers src, dst, and k, return the cheapest price
# from src to dst with at most k stops. If there is no such route, return -1.
#
# Example 1:
#
# Input: n = 4, flights = [[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]],
# src = 0, dst = 3, k = 1
# Output: 700
# Explanation:
# The graph is shown above.
# The optimal path with at most 1 stop from city 0 to 3 is marked in red and
# has cost 100 + 600 = 700.
# Note that the path through cities [0,1,2,3] is cheaper but is invalid because
# it uses 2 stops.
#
# Example 2:
#
# Input: n = 3, flights = [[0,1,100],[1,2,100],[0,2,500]], src = 0, dst = 2, k
# = 1
# Output: 200
# Explanation:
# The graph is shown above.
# The optimal path with at most 1 stop from city 0 to 2 is marked in red and
# has cost 100 + 100 = 200.
#
# Example 3:
#
# Input: n = 3, flights = [[0,1,100],[1,2,100],[0,2,500]], src = 0, dst = 2, k
# = 0
# Output: 500
# Explanation:
# The graph is shown above.
# The optimal path with no stops from city 0 to 2 is marked in red and has cost
# 500.
#
# Constraints:
#
# 2 <= n <= 100
#
# 0 <= flights.length <= (n * (n - 1) / 2)
#
# flights[i].length == 3
#
# 0 <= from_i, to_i < n
#
# from_i != to_i
#
# 1 <= price_i <= 10^4
#
# There will not be any multiple flights between two cities.
#
# 0 <= src, dst, k < n
#
# src != dst
#

# @lc code=start
import heapq
from collections import defaultdict
from typing import List


class Solution:
    def findCheapestPrice(
        self, n: int, flights: List[List[int]], src: int, dst: int, k: int
    ) -> int:
        """
        Interview explanation:
        Cheapest path from src to dst with at most k stops (= at most k+1 edges).
        Bellman-Ford: relax all edges for k+1 rounds using a dist snapshot so
        each round adds at most one hop.

        Algorithm (Bellman-Ford):
        - dist[src] = 0; others inf.
        - Repeat k+1 times: nxt = dist[:]; for each edge u→v,w:
          nxt[v] = min(nxt[v], dist[u]+w); dist = nxt.
        - Return dist[dst] or -1.

        Complexity: O((k+1) * E) time, O(n) space.
        """
        dist = [float("inf")] * n
        dist[src] = 0
        for _ in range(k + 1):
            nxt = dist[:]
            for u, v, w in flights:
                if dist[u] + w < nxt[v]:
                    nxt[v] = dist[u] + w
            dist = nxt
        return -1 if dist[dst] == float("inf") else int(dist[dst])

    def findCheapestPrice_dijkstra(
        self, n: int, flights: List[List[int]], src: int, dst: int, k: int
    ) -> int:
        """
        Interview explanation:
        Alternate: Dijkstra on (cost, city, stops). Heap ordered by cost; first
        time dst is popped is optimal. Prune states that reach a city with
        more/equal stops than a cheaper (already processed) visit.

        Algorithm:
        - Graph adjacency; heap (cost, u, stops); best_stops[u] = min stops
          among processed visits.
        - Pop; if u == dst return cost; if stops > k or stops >= best_stops[u]
          skip; else record and push neighbors with stops+1.

        Complexity: O(E * k * log(V*k)) time, O(V + E) space.
        """
        g = defaultdict(list)
        for u, v, w in flights:
            g[u].append((v, w))
        heap = [(0, src, 0)]  # cost, node, edges_used
        best_stops = [float("inf")] * n
        while heap:
            cost, u, stops = heapq.heappop(heap)
            if u == dst:
                return cost
            if stops > k or stops >= best_stops[u]:
                continue
            best_stops[u] = stops
            for v, w in g[u]:
                heapq.heappush(heap, (cost + w, v, stops + 1))
        return -1
# @lc code=end


