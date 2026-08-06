package leetcode

import "sort"

//
// LeetCode 1168 — Optimize Water Distribution In A Village
//
// --- Interview notes (graph modeling, MST, Kruskal, DSU, complexity, edges, alternatives) ---
//
// Problem (informal)
// `n` houses. Digging a well at house `i` costs `wells[i-1]` (1-indexed houses in statement). Undirected pipes connect
// pairs of houses with given costs. Every house must receive water: either it has its own well, or it is connected by
// pipes to some house that ultimately draws from a well. Minimize total spending (sum of chosen well costs + pipe costs).
//
// Graph model — virtual “water source” node
// Introduce node `0` representing “groundwater / central supply.” For each house `h ∈ {1,…,n}`, add edge `(0, h)` with
// weight `wells[h-1]`. Interpret digging a well at `h` as paying that edge to connect `h` to the source.
// Each pipe `[u, v, w]` is an undirected edge `(u, v)` with weight `w`.
// Any feasible construction connects every house to water ⇔ in this augmented graph with `n + 1` nodes, every house lies in
// the same connected component as node `0` ⇔ we have a connected subgraph spanning all `n + 1` nodes.
//
// Why minimum spanning tree?
// • Any connected graph contains a spanning tree whose total weight is **≤** that of the whole graph (drop redundant edges).
// • For nonnegative weights, an MST minimizes total edge weight among all spanning trees — exactly our objective once the
// modeling is correct: choose edges so all nodes {0,…,n} are connected for minimum sum.
// • **Tree suffices:** If a feasible network has a cycle, remove any pipe on the cycle; houses stay connected to water
// and cost drops. So an optimal solution exists as a **tree** on `{0,…,n}` — find MST.
//
// Algorithm — Kruskal
// 1. Collect all edges: virtual edges `(0, i)` with `wells[i-1]`, plus each pipe `(u, v, cost)`.
// 2. Sort edges by weight ascending.
// 3. Union–Find (Disjoint Set Union): iterate edges in order; if endpoints lie in different DSU sets, `union` them and add
//    weight to the answer. Stop after accepting **`n` edges** — an MST on `n + 1` vertices has exactly `n` edges.
//
// Data structures
// • **Edge list + sort** — Kruskal’s prerequisite.
// • **DSU** with path compression — near–`α(n)` amortized per operation (union by rank optional).
//
// Time complexity
// `E = len(pipes) + n` edges. Sorting dominates: **O(E log E)**. DSU operations **O(E α(n))** ⇒ overall **O(E log E)**.
//
// Space complexity
// **O(n)** for DSU parent array on `n + 1` nodes; **O(E)** for the edge list.
//
// Edge cases
// • `n = 1` — single edge `(0,1)` wins; answer `wells[0]`.
// • No pipes — MST uses only virtual edges; each house must attach to `0` directly ⇒ sum of `wells` only if no cheaper
//   linking exists—actually with no pipes, components are isolated houses; Kruskal connects each `i` to `0` via `(0,i)` in
//   increasing well cost order until all merged… wait with no pipes, we need n edges all from 0 to each house? That would
//   be n edges from 0 — but one edge (0,1) only connects house 1. We need each house i connected to 0; without pipes the
//   only edges are (0,i), so we must take all n edges (0,1),…,(0,n) — total sum(wells). Correct.
//
// Tests (statement-style)
// `n = 3`, `wells = [1,2,2]`, `pipes = [[1,2,1],[2,3,1]]` → **3** (e.g. well at house 1 + pipes 1–2 and 2–3).
//
// Alternative — Prim
// Start from node `0`, grow MST with a min-heap — **O(E log V)**. Equivalent answer; Kruskal is natural when all edges are
// listed up front.
//
// Improvements
// • Union by size/rank for DSU.
// • Early exit after `n` edges accepted (implemented below).
//
// --- end notes ---
//

type edge1168 struct {
	w int
	u int
	v int
}

type dsu1168 struct {
	parent []int
}

func newDSU1168(n int) *dsu1168 {
	p := make([]int, n)
	for i := range p {
		p[i] = i
	}
	return &dsu1168{parent: p}
}

func (d *dsu1168) find(x int) int {
	for d.parent[x] != x {
		d.parent[x] = d.parent[d.parent[x]]
		x = d.parent[x]
	}
	return x
}

func (d *dsu1168) union(a, b int) bool {
	ra := d.find(a)
	rb := d.find(b)
	if ra == rb {
		return false
	}
	d.parent[ra] = rb
	return true
}

// MinCostToSupplyWater1168 returns the minimum total cost to supply water to all houses.
func MinCostToSupplyWater1168(n int, wells []int, pipes [][]int) int {
	edges := make([]edge1168, 0, n+len(pipes))
	for i, w := range wells {
		edges = append(edges, edge1168{w: w, u: 0, v: i + 1})
	}
	for _, p := range pipes {
		edges = append(edges, edge1168{w: p[2], u: p[0], v: p[1]})
	}
	sort.Slice(edges, func(i, j int) bool { return edges[i].w < edges[j].w })

	dsu := newDSU1168(n + 1)
	total := 0
	used := 0
	for _, e := range edges {
		if dsu.union(e.u, e.v) {
			total += e.w
			used++
			if used == n {
				break
			}
		}
	}
	return total
}

