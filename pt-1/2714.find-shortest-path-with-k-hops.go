package leetcode

//
// @lc app=leetcode id=2714 lang=golang
//
// [2714] Find Shortest Path with K Hops
//
// --- Interview notes (statement, layered graph, Dijkstra, complexity, edges, tests) ---
//
// Problem (summary)
// Undirected weighted connected graph on n nodes (0 .. n-1). You may choose up to k edges on your walk and
// treat their weights as 0 (each such edge still counts as one step — “hop” here means zeroing that edge’s
// contribution to cost). Find the minimum total cost of a walk from source s to destination d.
//
// Equivalent layered shortest path
// Expand each vertex u into (k+1) states (u, t) meaning:
//   “we have arrived at node u having already used exactly t zero-cost edges along the path taken so far.”
// Transitions from state (u, t) along undirected edge (u, v) with weight w:
//   (A) Pay the edge: go to (v, t) with added cost w.
//   (B) If t < k, zero the edge: go to (v, t + 1) with added cost 0.
// All edge weights in the expanded graph are non-negative → Dijkstra applies on states (u, t).
//
// Why not plain Dijkstra on the original graph
// Original graph does not encode how many free edges remain; that resource couples choices — classic
// shortest path with a small integer resource → DP dimension or layered graph.
//
// Algorithm
// - Build adjacency lists for the undirected graph.
// - dist[u][t] = best known cost to reach u with exactly t free edges used (initialize ∞ except dist[s][0]=0).
// - Priority queue of (cost, u, t); pop smallest; relax neighbors:
//     nd = cost + w  → relax (v, t)
//     if t < k: relax (v, t+1) at same cost (hop / zero-weight edge).
// - Answer = min_t dist[d][t].
//
// Data structures
// - Adjacency list: O(n + |E|).
// - dist: n × (k+1) table (or sparse map if needed — here explicit table is fine).
// - Min-heap for Dijkstra.
//
// Time complexity
// States: O(n · k). Each undirected edge examined from each (u,t) at most when that state is finalized —
// roughly O(|E| · k) relaxations in practice; heap pushes bounded similarly → O(|E| · k · log(n · k)) typical.
//
// Space complexity
// O(n · k + |E|) for distances + graph.
//
// Alternatives (interview variants)
// - Bellman–Ford style: repeat relaxation k+1 rounds on implicit layered edges — O(|E| · k · (k+1)) variants;
//   Dijkstra preferred when all expanded weights are non-negative (they are).
// - If k were huge but special structure, other tricks — not needed under usual constraints.
//
// Edge cases
// - s == d: answer 0 (dist[s][0] = 0).
// - k == 0: ordinary shortest path from s to d.
// - Using a hop on a zero-weight edge: allowed but never worsens cost.
//
// Tests (mental / small)
// - n=2, edge weight W, k>=1: answer 0 if hop used on that edge.
// - Line graph with large weights: optimal deployment of k zeros along path — matches brute force on tiny n.
//
// Improvements
// - Early exit when destination extracted with minimal possible layer — optional micro-optimization.
//
// --- end notes ---
//
// @lc code=start

import "container/heap"

type _edge2714 struct {
	to int
	w  int
}

type _state2714 struct {
	d int64
	u int
	t int
}

type _pq2714 []_state2714

func (p _pq2714) Len() int            { return len(p) }
func (p _pq2714) Less(i, j int) bool  { return p[i].d < p[j].d }
func (p _pq2714) Swap(i, j int)       { p[i], p[j] = p[j], p[i] }
func (p *_pq2714) Push(x any)         { *p = append(*p, x.(_state2714)) }
func (p *_pq2714) Pop() any           { old := *p; x := old[len(old)-1]; *p = old[:len(old)-1]; return x }

// ShortestPathWithHops2714 returns the minimum cost from s to d when up to k edges
// along the route may be made free (weight 0).
func ShortestPathWithHops2714(n int, edges [][]int, s int, d int, k int) int64 {
	g := make([][]_edge2714, n)
	for _, e := range edges {
		u, v, w := e[0], e[1], e[2]
		g[u] = append(g[u], _edge2714{to: v, w: w})
		g[v] = append(g[v], _edge2714{to: u, w: w})
	}

	const inf int64 = 1<<62
	dist := make([][]int64, n)
	for i := 0; i < n; i++ {
		dist[i] = make([]int64, k+1)
		for t := 0; t <= k; t++ {
			dist[i][t] = inf
		}
	}
	dist[s][0] = 0

	pq := &_pq2714{{d: 0, u: s, t: 0}}
	heap.Init(pq)

	for pq.Len() > 0 {
		cur := heap.Pop(pq).(_state2714)
		if cur.d != dist[cur.u][cur.t] {
			continue
		}
		for _, ed := range g[cur.u] {
			nd := cur.d + int64(ed.w)
			if nd < dist[ed.to][cur.t] {
				dist[ed.to][cur.t] = nd
				heap.Push(pq, _state2714{d: nd, u: ed.to, t: cur.t})
			}
			if cur.t < k {
				if cur.d < dist[ed.to][cur.t+1] {
					dist[ed.to][cur.t+1] = cur.d
					heap.Push(pq, _state2714{d: cur.d, u: ed.to, t: cur.t + 1})
				}
			}
		}
	}

	best := dist[d][0]
	for t := 1; t <= k; t++ {
		if dist[d][t] < best {
			best = dist[d][t]
		}
	}
	return best
}

// @lc code=end

