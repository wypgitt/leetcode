#
# @lc app=leetcode id=2642 lang=python3
#
# [2642] Design Graph With Shortest Path Calculator
#

# --- Notes (API, modeling, Dijkstra vs Floyd, heap, complexity, edges, interview) ---
#
# Problem / API
# - Directed weighted graph with n nodes labeled 0 .. n-1.
# - `Graph(n, edges)` builds initial adjacency from `edges`, each edge `[u, v, w]` meaning u -> v with
#   nonnegative weight w (LeetCode uses positive costs in examples; Dijkstra requires nonnegative).
# - `addEdge([u, v, w])` appends another directed edge (parallel edges allowed).
# - `shortestPath(node1, node2)` returns minimum total edge weight along any directed path from
#   node1 to node2, or -1 if unreachable. Convention: shortest path from a node to itself is 0.
#
# Why Dijkstra on each query?
# - Edges are appended over time; the graph grows but stays sparse in typical tests.
# - Running Dijkstra from `node1` whenever `shortestPath` is called costs O((V + E) log V) with a
#   binary heap — simple, correct for nonnegative weights, no separate update logic when edges are added.
# - Alternative: maintain all-pairs shortest paths with Floyd–Warshall (O(n^3) setup, O(n^2) per
#   `addEdge` relaxation, O(1) query). Better only when n is small and queries vastly outnumber adds.
#
# Algorithm (Dijkstra)
# - Single-source shortest paths from `node1`: dist[x] = best known cost to reach x.
# - Min-heap ordered by tentative distance; pop smallest (lazy deletion when stale entries appear).
# - Relax outgoing edges (v, w) from u: if dist[u] + w < dist[v], update and push.
# - Stop early optional when node2 popped — implemented by checking when we extract node2 (first time
#   is optimal).
#
# Data structures
# - Adjacency list: `list[list[tuple[int,int]]]` — O(V + E) memory, fast iteration of out-edges.
# - `heapq` min-heap of `(distance, node)` pairs.
# - `dist` array length n, initialized to +infinity except source 0.
#
# Time complexity
# - `__init__`: O(n + |initial edges|).
# - `addEdge`: O(1) amortized append.
# - `shortestPath`: O((V + E') log V) where E' is edges present at query time (standard Dijkstra).
#
# Space complexity
# - O(V + E) for the graph plus O(V) for dist and O(E) heap worst-case — dominated by graph storage.
#
# Edge cases
# - node1 == node2 -> return 0 without searching.
# - Disconnected target -> heap empties, dist[node2] still inf -> -1.
# - Multiple edges u -> v: adjacency list keeps all; Dijkstra naturally picks cheapest combination.
#
# Improvements / variants
# - For tiny n and many queries: Floyd–Warshall incremental updates (see editorial).
# - For integer weights small: Dial’s algorithm (bucket deque) can replace heap.
# - Early exit: break when popped node == node2 (optional micro-optimization).
#
# LeetCode submission
# Put imports (`heapq`, `math`, `typing.List`) inside the LC code section markers.
#
# Interview walkthrough
# 1) Dynamic graph + shortest path queries -> incremental APSP vs on-demand SSSP.
# 2) Nonnegative weights -> Dijkstra; cite why not Bellman-Ford here.
# 3) Adjacency list + heap complexity.
# 4) Mention Floyd trade-off when interview asks for faster queries at small n.
# --- end notes ---

# @lc code=start
import heapq
import math
from typing import List


class Graph:
    def __init__(self, n: int, edges: List[List[int]]) -> None:
        """
        Interview explanation:
        Build a directed weighted graph on n nodes from the initial edge list.

        Algorithm:
        - Store an adjacency list of (neighbor, weight) pairs; append each [u, v, w].

        Complexity: O(n + |edges|) time, O(n + |edges|) space.
        """
        self._n = n
        self._g: List[List[tuple[int, int]]] = [[] for _ in range(n)]
        for u, v, w in edges:
            self._g[u].append((v, w))

    def addEdge(self, edge: List[int]) -> None:
        """
        Interview explanation:
        Append a directed edge [u, v, w] to the live graph (parallel edges allowed).

        Algorithm:
        - Append (v, w) to u's adjacency list; no APSP update needed with on-demand Dijkstra.

        Complexity: O(1) time, O(1) space.
        """
        u, v, w = edge
        self._g[u].append((v, w))

    def shortestPath(self, node1: int, node2: int) -> int:
        """
        Interview explanation:
        Return the minimum path weight from node1 to node2, or -1 if unreachable
        (0 when node1 == node2). Nonnegative weights → Dijkstra per query.

        Algorithm:
        - Binary-heap Dijkstra from node1; lazy skip of stale heap entries; early exit
          when node2 is first extracted. (Floyd–Warshall is an alternate for tiny n.)

        Complexity: O((V + E) log V) time, O(V + E) space.
        """
        if node1 == node2:
            return 0
        dist = [math.inf] * self._n
        dist[node1] = 0
        heap: List[tuple[float, int]] = [(0.0, node1)]
        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            if u == node2:
                return int(d)
            for v, w in self._g[u]:
                nd = d + w
                if nd < dist[v]:
                    dist[v] = nd
                    heapq.heappush(heap, (nd, v))
        return -1


# Your Graph object will be instantiated and called as such:
# obj = Graph(n, edges)
# obj.addEdge(edge)
# param_2 = obj.shortestPath(node1,node2)
# @lc code=end
