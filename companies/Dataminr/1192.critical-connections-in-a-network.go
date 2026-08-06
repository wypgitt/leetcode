package leetcode

import "sort"

//
// LeetCode 1192 — Critical Connections In A Network
//
// --- Interview notes (bridges, Tarjan DFS, low-link, complexity, multigraph caveat, tests) ---
//
// Problem
// Undirected connected graph on `n` labeled vertices `0 … n-1`. **Critical connections** (bridges) are edges whose removal
// increases the number of connected components — equivalently, edges that belong to **no** simple cycle.
//
// Why Tarjan / DFS low-link (not BFS alone)
// We need structural information about cycles vs tree edges in a DFS spanning forest. **Discovery times** and **low values**
// summarize, per subtree, whether there is a back edge to an ancestor — the classical **O(V+E)** bridge algorithm.
//
// Definitions (DFS from an arbitrary root)
// • `disc[u]` — discovery time / preorder stamp when `u` is first visited (1-based counter here).
// • `low[u]` — minimum discovery time reachable from `u` using **zero or more tree edges down** plus **at most one back edge
//   up** to an ancestor (standard low-link for undirected bridge detection).
//
// Bridge criterion (tree edge u → v, where `v` is a child of `u` in DFS tree)
// Edge `(u, v)` is a bridge **iff** `low[v] > disc[u]`.
// Interpretation: everything reachable from `v` without using edge `(u,v)` stays strictly below `u` in DFS order — no back
// edge from `v`’s subtree hooks to `u` or above. Removing `(u,v)` isolates that subtree.
//
// Back edges
// When exploring `u` and hitting a visited neighbor `w` that is **not** the DFS parent, update `low[u] = min(low[u],
// disc[w])` (edge to an ancestor or already discovered vertex in undirected graph).
//
// Algorithm
// 1. Build adjacency lists.
// 2. Run one DFS (or from every unvisited vertex if the graph might be disconnected — still correct).
// 3. After recursive call returns from child `v`, set `low[u] = min(low[u], low[v])` and test bridge condition.
//
// Data structures
// • **Adjacency list** — `O(V+E)` space, optimal traversal.
// • **Arrays `disc`, `low`** — `O(V)`.
// • **Output list** — `O(E)` worst case (at most `V-1` bridges in a tree).
//
// Time complexity **O(V + E)** — each vertex and edge examined constant times.
//
// Space complexity **O(V + E)** for graph + recursion stack **O(V)** (worst path depth).
//
// Multigraph caveat (parallel edges)
// If two **parallel** edges connect the same endpoints, neither is a bridge; the naive `if v == parent: continue` skips **all**
// edges to the parent and mis-handles the second parallel edge. Fixes: traverse **edge ids**, or count parent skips.
// LeetCode inputs are typically **simple** graphs (at most one edge per unordered pair); this solution assumes that.
//
// Edge cases
// • Tree on `n` nodes — every edge is a bridge (`n-1` bridges).
// • Single cycle — **no** bridges.
// • `n = 2`, one edge — that edge is critical.
//
// Tests (sanity)
// • `n = 4`, `connections = [[0,1],[1,2],[2,0],[1,3]]` → triangle plus leaf: only **`[1,3]`** is a bridge.
//
// Improvements
// • Iterative DFS if recursion depth exceeds Python limit on very long paths (rare with constraints).
// • Tarjan also finds articulation points with a small extension — related interview topic.
//
// --- end notes ---
//

// CriticalConnections1192 returns all bridges in sorted order.
func CriticalConnections1192(n int, connections [][]int) [][]int {
	g := make([][]int, n)
	for _, e := range connections {
		a, b := e[0], e[1]
		g[a] = append(g[a], b)
		g[b] = append(g[b], a)
	}

	disc := make([]int, n)
	low := make([]int, n)
	t := 1
	bridges := make([][]int, 0)

	var dfs func(u, parent int)
	dfs = func(u, parent int) {
		disc[u] = t
		low[u] = t
		t++
		for _, v := range g[u] {
			if v == parent {
				continue
			}
			if disc[v] == 0 {
				dfs(v, u)
				if low[v] < low[u] {
					low[u] = low[v]
				}
				if low[v] > disc[u] {
					a, b := u, v
					if a > b {
						a, b = b, a
					}
					bridges = append(bridges, []int{a, b})
				}
			} else if disc[v] < low[u] {
				low[u] = disc[v]
			}
		}
	}

	for i := 0; i < n; i++ {
		if disc[i] == 0 {
			dfs(i, -1)
		}
	}

	sort.Slice(bridges, func(i, j int) bool {
		if bridges[i][0] != bridges[j][0] {
			return bridges[i][0] < bridges[j][0]
		}
		return bridges[i][1] < bridges[j][1]
	})
	return bridges
}

