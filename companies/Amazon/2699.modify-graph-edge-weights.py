#
# @lc app=leetcode id=2699 lang=python3
#
# [2699] Modify Graph Edge Weights
#

# --- Interview notes (statement, reasoning, algorithm, DS, complexity, edges, tests) ---
#
# Problem (summary)
# Undirected connected graph on n nodes; edges[i] = [u, v, w]. Some weights are fixed positives;
# some are w = -1 and must be replaced by an integer in [1, 2 * 10^9]. You may NOT change fixed edges.
# Goal: assign every -1 so that the shortest-path distance from source to destination equals target.
# Return the full edge list (any order) with all weights filled in, or [] if impossible.
#
# Core observations
# 1) Increasing an edge weight cannot shorten any path — only lengthen or leave unchanged. Decreasing (down
#    to the minimum allowed 1) can only shorten paths that use that edge.
# 2) Ignoring all -1 edges gives the shortest paths that use only original positive edges. Call that
#    distance d_pos. If d_pos < target, then those paths still exist no matter how we weight -1 edges
#    (weights are ≥ 1, so they cannot “block” the fixed-edge routes). The global shortest distance can
#    never become target — it stays ≤ d_pos < target → impossible → return [].
# 3) If d_pos == target, we are already done with distance; set every remaining -1 to a huge weight
#    (here 2 * 10^9) so no cheap shortcut appears through them (still within allowed range).
# 4) If d_pos > target (or +∞ when no positive-only path exists), we must use -1 edges as cheap links
#    (weight 1 is minimal) to pull the shortest distance down toward target.
#
# Greedy construction (editorial / contest solution)
# Maintain flag ok meaning “we already achieved shortest distance ≤ target”.
# Scan edges in given order; for each undecided edge (w == -1):
#   - If ok: assign INF (2e9) so this edge is never useful as a shortcut vs earlier choices.
#   - Else: temporarily set this edge to 1, run single-source shortest paths from source (Dijkstra —
#     non-negative weights). Let d be dist[destination].
#          If d ≤ target: set ok true; increase THIS edge by (target - d) so that the overall shortest
#          distance becomes exactly d + (target - d) = target (only this edge’s increment applies along
#          the tightened shortest route in the standard proof sketch).
#          If d > target: leave weight at 1 for now (still cheapest) and try later edges.
# After processing, ok must be true; else no assignment worked → [].
#
# Why Dijkstra (not Bellman–Ford)
# All realized edge weights are positive integers (≥ 1); graph is undirected for relaxation both ways.
#
# Implementation choice — adjacency list + binary heap Dijkstra
# - n ≤ 100 but m can be Θ(n^2); heap version is O((n + m) log n) per run and simple in Python.
# - Alternative: dense O(n^2) Dijkstra / Floyd-Warshall — also fine at this scale.
#
# Time complexity
# One initial Dijkstra + up to one per “-1” edge → O(E · (m log n)) with heap, which is easily fast for
# n ≤ 100 (worst-case ~10^4 edges, trivial).
#
# Space complexity
# O(n + m) for graph + dist arrays + heap.
#
# Edge cases (talk through)
# - d_pos < target → [] immediately (Example 2 path 0–2 weight 5 but target 6 cannot be forced larger).
# - No positive-only path (d_pos = ∞): still possible using flexible edges only after assigning some to 1.
# - Multiple valid outputs: Example 1-style assignments differ in which edge absorbs slack; any valid list passes.
#
# Tests (examples from statement)
# Ex1 n=5, edges with four -1’s, source=0 dest=1 target=5 → non-empty assignment.
# Ex2 → [] as above.
# Ex3 → includes [0,3,1] with shortest 0–2 distance 6.
#
# Improvements
# - Early exit when ok becomes true and remaining -1 edges only need INF (already done).
# - Could reuse potentials / incremental shortest paths — unnecessary at n = 100.
#
# --- end notes ---

# @lc code=start

import heapq
from typing import List


class Solution:
    def modifiedGraphEdges(
        self,
        n: int,
        edges: List[List[int]],
        source: int,
        destination: int,
        target: int,
    ) -> List[List[int]]:
        """
        Interview explanation:
        Undirected graph; some edge weights are -1 (assign in [1, 2e9]) so shortest path source→dest
        equals target. Return filled edges or [] if impossible.

        Algorithm:
        - Dijkstra on positive edges; if dist < target impossible; if == target set -1 to INF.
          Else greedily set each -1 to 1, Dijkstra; when dist <= target bump that edge by target-dist.

        Complexity: O(E * (V+E) log V) time, O(V+E) space.
        """
        inf = 2 * 10**9

        def dijkstra() -> int:
            g = [[] for _ in range(n)]
            for a, b, w in edges:
                if w == -1:
                    continue
                g[a].append((b, w))
                g[b].append((a, w))
            dist = [inf] * n
            dist[source] = 0
            pq = [(0, source)]
            while pq:
                d, u = heapq.heappop(pq)
                if d != dist[u]:
                    continue
                for v, w in g[u]:
                    nd = d + w
                    if nd < dist[v]:
                        dist[v] = nd
                        heapq.heappush(pq, (nd, v))
            return dist[destination]

        d = dijkstra()
        if d < target:
            return []

        ok = d == target
        for e in edges:
            if e[2] > 0:
                continue
            if ok:
                e[2] = inf
                continue
            e[2] = 1
            d = dijkstra()
            if d <= target:
                ok = True
                e[2] += target - d

        return edges if ok else []
# @lc code=end
