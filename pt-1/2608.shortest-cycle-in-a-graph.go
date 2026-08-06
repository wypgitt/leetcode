package leetcode

//
// LeetCode 2608 — Shortest Cycle in a Graph
//
// --- Notes (problem, undirected cycle, BFS idea, parent check, complexity, tests, edges, interview) ---
//
// Problem restatement
// Undirected graph with n vertices labeled 0..n-1 and edge list `edges`. Each edge is used at most
// once in a simple cycle. Return the length (number of edges) of the SHORTEST cycle, or -1 if the
// graph is acyclic (forest). For unweighted graphs, “shortest” = fewest edges.
//
// Why BFS (not DFS length alone)?
// Edge weights are uniform (each edge length 1). Shortest paths from a source are found by BFS.
// Shortest cycle length relates to shortest paths between nodes on the cycle — BFS layers encode
// distances from the root of that search.
//
// Core algorithm — BFS from every vertex (shortest odd/even cycle cover)
// Fact (standard): In an undirected unweighted graph, the global shortest cycle length equals the
// minimum over all choices of root `s` of “shortest cycle that BFS from s discovers via the first
// non-tree cross edge” — equivalently, take min over all roots of BFS-and-detect (some write-ups
// prove considering each vertex as root suffices to hit every shortest cycle’s smallest vertex).
// Practical LC solution: run BFS starting from each vertex `s` in {0..n-1}, maintain `dist[]` =
// shortest distance from `s` (-1 / INF if unreachable in this BFS tree component exploration).
//
// Detecting a cycle while expanding from `s`
// Pop vertex `u`, scan neighbor `v`:
//   - If `v` not visited in this BFS: set dist[v] = dist[u] + 1, push `v`.
//   - Else `v` already visited: if `(v, u)` is NOT just the tree edge back to the parent of `u`,
//     then edge `(u, v)` closes a cycle. Length = dist[u] + dist[v] + 1 (walk from s to u, edge u-v,
//     walk v to s — meets at s forming a simple cycle in an unweighted graph when distances are
//     shortest-layer distances from s).
// Parent / tree-edge exclusion (undirected):
//   If `v` is the parent of `u` on the BFS tree rooted at `s`, then dist[v] = dist[u] - 1, i.e.
//   dist[v] + 1 == dist[u]. So we ONLY treat as a cycle when:
//       dist[v] + 1 != dist[u]
//   This ignores the backward tree edge; cross edges between layers or same layer trigger update.
//
// Implementation detail
// Some references return on first hit during BFS(s); that is often fine. To be safe, take the
// minimum over ALL cross-edge detections within one BFS(s) (multiple cycles through s possible in
// weird orders). Globally answer = min_s BFS(s).
//
// Data structures
// - Adjacency list: list[list[int]] of size n — O(n + m) space, O(1) neighbor iteration overhead.
// - Queue (collections.deque) for BFS — O(n) per BFS.
// - dist array length n per BFS — O(n) space per pass.
//
// Time complexity
// - Build graph: O(n + m).
// - For each of n sources, BFS visits each edge at most twice (both endpoints): O(n * (n + m)).
//   With constraints like n, m <= 1000 (typical), this fits easily.
//
// Space complexity
// - O(n + m) for adjacency list plus O(n) for each BFS queue/dist — dominated by O(n + m).
//
// Alternative approaches (interview talking points)
// - Remove each edge, BFS shortest path between endpoints; cycle length = path + 1. O(m * (n+m)).
// - For planar / special graphs, faster structures exist; general sparse graphs often use the
//   multi-source BFS-on-every-node method above for clarity.
//
// Edge cases
// - Tree (no cycle): every BFS finds no cross edge -> return -1.
// - Single cycle component: BFS from any vertex on that cycle finds it.
// - Disconnected graph: BFS from each node still covers each component when rooted inside it.
// - Multi-edges between u and v: adjacency list lists both; may form a 2-cycle — dist logic still
//   yields length 2 when applicable.
// - n < 2 or empty edges: no cycle -> -1 (constraints usually guarantee at least one edge when cycle
//   exists; still handle gracefully).
//
// Tests (small)
// - Triangle 0-1-2-0: shortest cycle length 3.
// - Square 0-1-2-3-0: shortest cycle 4.
// - Two parallel edges between 0 and 1: cycle length 2.
//
// LeetCode submission
// Put `from typing import List` and `import collections` inside # @lc code=start so submit bundle works.
//
// Interview walkthrough
// 1) Unweighted shortest cycle -> think BFS distances.
// 2) Fix root s; tree edge vs cross edge via dist relation dist[v]+1 vs dist[u].
// 3) Min over all roots; argue shortest cycle is discovered.
// 4) Complexity O(n(n+m)); mention edge-removal BFS as alternative trade-off.
// --- end notes ---
//

// FindShortestCycle2608 returns the length of the shortest cycle in the graph, or -1.
func FindShortestCycle2608(n int, edges [][]int) int {
	g := make([][]int, n)
	for _, e := range edges {
		u, v := e[0], e[1]
		g[u] = append(g[u], v)
		g[v] = append(g[v], u)
	}
	const inf = int(1e9)

	bfs := func(src int) int {
		dist := make([]int, n)
		for i := range dist {
			dist[i] = -1
		}
		dist[src] = 0
		q := make([]int, 0, n)
		q = append(q, src)
		head := 0
		best := inf
		for head < len(q) {
			u := q[head]
			head++
			for _, v := range g[u] {
				if dist[v] == -1 {
					dist[v] = dist[u] + 1
					q = append(q, v)
				} else if dist[v]+1 != dist[u] {
					cand := dist[u] + dist[v] + 1
					if cand < best {
						best = cand
					}
				}
			}
		}
		return best
	}

	ans := inf
	for s := 0; s < n; s++ {
		if v := bfs(s); v < ans {
			ans = v
		}
	}
	if ans >= inf {
		return -1
	}
	return ans
}

