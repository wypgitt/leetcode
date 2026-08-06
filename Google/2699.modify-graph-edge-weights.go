package leetcode

//
// @lc app=leetcode id=2699 lang=golang
//
// [2699] Modify Graph Edge Weights
//
// --- Interview notes (statement, reasoning, algorithm, DS, complexity, edges, tests) ---
//
// Problem (summary)
// Undirected connected graph on n nodes; edges[i] = [u, v, w]. Some weights are fixed positives;
// some are w = -1 and must be replaced by an integer in [1, 2 * 10^9]. You may NOT change fixed edges.
// Goal: assign every -1 so that the shortest-path distance from source to destination equals target.
// Return the full edge list (any order) with all weights filled in, or [] if impossible.
//
// Core observations
// 1) Increasing an edge weight cannot shorten any path — only lengthen or leave unchanged. Decreasing (down
//    to the minimum allowed 1) can only shorten paths that use that edge.
// 2) Ignoring all -1 edges gives the shortest paths that use only original positive edges. Call that
//    distance d_pos. If d_pos < target, then those paths still exist no matter how we weight -1 edges
//    (weights are ≥ 1, so they cannot “block” the fixed-edge routes). The global shortest distance can
//    never become target — it stays ≤ d_pos < target → impossible → return [].
// 3) If d_pos == target, we are already done with distance; set every remaining -1 to a huge weight
//    (here 2 * 10^9) so no cheap shortcut appears through them (still within allowed range).
// 4) If d_pos > target (or +∞ when no positive-only path exists), we must use -1 edges as cheap links
//    (weight 1 is minimal) to pull the shortest distance down toward target.
//
// Greedy construction (editorial / contest solution)
// Maintain flag ok meaning “we already achieved shortest distance ≤ target”.
// Scan edges in given order; for each undecided edge (w == -1):
//   - If ok: assign INF (2e9) so this edge is never useful as a shortcut vs earlier choices.
//   - Else: temporarily set this edge to 1, run single-source shortest paths from source (Dijkstra —
//     non-negative weights). Let d be dist[destination].
//          If d ≤ target: set ok true; increase THIS edge by (target - d) so that the overall shortest
//          distance becomes exactly d + (target - d) = target (only this edge’s increment applies along
//          the tightened shortest route in the standard proof sketch).
//          If d > target: leave weight at 1 for now (still cheapest) and try later edges.
// After processing, ok must be true; else no assignment worked → [].
//
// Why Dijkstra (not Bellman–Ford)
// All realized edge weights are positive integers (≥ 1); graph is undirected for relaxation both ways.
//
// Implementation choice — adjacency list + binary heap Dijkstra
// - n ≤ 100 but m can be Θ(n^2); heap version is O((n + m) log n) per run and simple in Go.
// - Alternative: dense O(n^2) Dijkstra / Floyd-Warshall — also fine at this scale.
//
// Time complexity
// One initial Dijkstra + up to one per “-1” edge → O(E · (m log n)) with heap, which is easily fast for
// n ≤ 100 (worst-case ~10^4 edges, trivial).
//
// Space complexity
// O(n + m) for graph + dist arrays + heap.
//
// Edge cases (talk through)
// - d_pos < target → [] immediately (Example 2 path 0–2 weight 5 but target 6 cannot be forced larger).
// - No positive-only path (d_pos = ∞): still possible using flexible edges only after assigning some to 1.
// - Multiple valid outputs: Example 1-style assignments differ in which edge absorbs slack; any valid list passes.
//
// Tests (examples from statement)
// Ex1 n=5, edges with four -1’s, source=0 dest=1 target=5 → non-empty assignment.
// Ex2 → [] as above.
// Ex3 → includes [0,3,1] with shortest 0–2 distance 6.
//
// Improvements
// - Early exit when ok becomes true and remaining -1 edges only need INF (already done).
// - Could reuse potentials / incremental shortest paths — unnecessary at n = 100.
//
// --- end notes ---
//
// @lc code=start

import "container/heap"

type _edge2699 struct {
	to int
	w  int
}

type _state2699 struct {
	d int64
	u int
}

type _pq2699 []_state2699

func (p _pq2699) Len() int            { return len(p) }
func (p _pq2699) Less(i, j int) bool  { return p[i].d < p[j].d }
func (p _pq2699) Swap(i, j int)       { p[i], p[j] = p[j], p[i] }
func (p *_pq2699) Push(x any)         { *p = append(*p, x.(_state2699)) }
func (p *_pq2699) Pop() any           { old := *p; x := old[len(old)-1]; *p = old[:len(old)-1]; return x }

// ModifiedGraphEdges2699 fills in all -1 edge weights so that the shortest path from source
// to destination equals target, or returns nil if impossible.
func ModifiedGraphEdges2699(n int, edges [][]int, source int, destination int, target int) [][]int {
	const inf int64 = 2_000_000_000

	dijkstra := func() int64 {
		g := make([][]_edge2699, n)
		for _, e := range edges {
			a, b, w := e[0], e[1], e[2]
			if w == -1 {
				continue
			}
			g[a] = append(g[a], _edge2699{to: b, w: w})
			g[b] = append(g[b], _edge2699{to: a, w: w})
		}

		dist := make([]int64, n)
		for i := 0; i < n; i++ {
			dist[i] = inf
		}
		dist[source] = 0
		pq := &_pq2699{{d: 0, u: source}}
		heap.Init(pq)

		for pq.Len() > 0 {
			cur := heap.Pop(pq).(_state2699)
			if cur.d != dist[cur.u] {
				continue
			}
			for _, ed := range g[cur.u] {
				nd := cur.d + int64(ed.w)
				if nd < dist[ed.to] {
					dist[ed.to] = nd
					heap.Push(pq, _state2699{d: nd, u: ed.to})
				}
			}
		}
		return dist[destination]
	}

	d := dijkstra()
	if d < int64(target) {
		return nil
	}

	ok := d == int64(target)
	for _, e := range edges {
		if e[2] > 0 {
			continue
		}
		if ok {
			e[2] = int(inf)
			continue
		}
		e[2] = 1
		d = dijkstra()
		if d <= int64(target) {
			ok = true
			e[2] += target - int(d)
		}
	}

	if !ok {
		return nil
	}
	return edges
}

// @lc code=end

