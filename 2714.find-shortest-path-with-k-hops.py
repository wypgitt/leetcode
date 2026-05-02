#
# @lc app=leetcode id=2714 lang=python3
#
# [2714] Find Shortest Path with K Hops
#

# --- Interview notes (statement, layered graph, Dijkstra, complexity, edges, tests) ---
#
# Problem (summary)
# Undirected weighted connected graph on n nodes (0 .. n-1). You may choose up to k edges on your walk and
# treat their weights as 0 (each such edge still counts as one step — “hop” here means zeroing that edge’s
# contribution to cost). Find the minimum total cost of a walk from source s to destination d.
#
# Equivalent layered shortest path
# Expand each vertex u into (k+1) states (u, t) meaning:
#   “we have arrived at node u having already used exactly t zero-cost edges along the path taken so far.”
# Transitions from state (u, t) along undirected edge (u, v) with weight w:
#   (A) Pay the edge: go to (v, t) with added cost w.
#   (B) If t < k, zero the edge: go to (v, t + 1) with added cost 0.
# All edge weights in the expanded graph are non-negative → Dijkstra applies on states (u, t).
#
# Why not plain Dijkstra on the original graph
# Original graph does not encode how many free edges remain; that resource couples choices — classic
# shortest path with a small integer resource → DP dimension or layered graph.
#
# Algorithm
# - Build adjacency lists for the undirected graph.
# - dist[u][t] = best known cost to reach u with exactly t free edges used (initialize ∞ except dist[s][0]=0).
# - Priority queue of (cost, u, t); pop smallest; relax neighbors:
#     nd = cost + w  → relax (v, t)
#     if t < k: relax (v, t+1) at same cost (hop / zero-weight edge).
# - Answer = min_t dist[d][t].
#
# Data structures
# - Adjacency list: O(n + |E|).
# - dist: n × (k+1) table (or sparse map if needed — here explicit table is fine).
# - Min-heap for Dijkstra.
#
# Time complexity
# States: O(n · k). Each undirected edge examined from each (u,t) at most when that state is finalized —
# roughly O(|E| · k) relaxations in practice; heap pushes bounded similarly → O(|E| · k · log(n · k)) typical.
#
# Space complexity
# O(n · k + |E|) for distances + graph.
#
# Alternatives (interview variants)
# - Bellman–Ford style: repeat relaxation k+1 rounds on implicit layered edges — O(|E| · k · (k+1)) variants;
#   Dijkstra preferred when all expanded weights are non-negative (they are).
# - If k were huge but special structure, other tricks — not needed under usual constraints.
#
# Edge cases
# - s == d: answer 0 (dist[s][0] = 0).
# - k == 0: ordinary shortest path from s to d.
# - Using a hop on a zero-weight edge: allowed but never worsens cost.
#
# Tests (mental / small)
# - n=2, edge weight W, k>=1: answer 0 if hop used on that edge.
# - Line graph with large weights: optimal deployment of k zeros along path — matches brute force on tiny n.
#
# Improvements
# - Early exit when destination extracted with minimal possible layer — optional micro-optimization.
#
# --- end notes ---

# @lc code=start
import heapq
from typing import List


class Solution:
    def shortestPathWithHops(self, n: int, edges: List[List[int]], s: int, d: int, k: int) -> int:
        g = [[] for _ in range(n)]
        for u, v, w in edges:
            g[u].append((v, w))
            g[v].append((u, w))

        inf = 10**18
        dist = [[inf] * (k + 1) for _ in range(n)]
        dist[s][0] = 0
        pq = [(0, s, 0)]

        while pq:
            du, u, t = heapq.heappop(pq)
            if du > dist[u][t]:
                continue
            for v, w in g[u]:
                nd = du + w
                if nd < dist[v][t]:
                    dist[v][t] = nd
                    heapq.heappush(pq, (nd, v, t))
                if t < k:
                    nd = du
                    if nd < dist[v][t + 1]:
                        dist[v][t + 1] = nd
                        heapq.heappush(pq, (nd, v, t + 1))

        return min(dist[d])


# @lc code=end
