package leetcode

//
// @lc app=leetcode id=2642 lang=golang
//
// [2642] Design Graph With Shortest Path Calculator
//
// --- Notes (API, modeling, Dijkstra vs Floyd, heap, complexity, edges, interview) ---
//
// Problem / API
// - Directed weighted graph with n nodes labeled 0 .. n-1.
// - `Graph(n, edges)` builds initial adjacency from `edges`, each edge `[u, v, w]` meaning u -> v with
//   nonnegative weight w (LeetCode uses positive costs in examples; Dijkstra requires nonnegative).
// - `addEdge([u, v, w])` appends another directed edge (parallel edges allowed).
// - `shortestPath(node1, node2)` returns minimum total edge weight along any directed path from
//   node1 to node2, or -1 if unreachable. Convention: shortest path from a node to itself is 0.
//
// Why Dijkstra on each query?
// - Edges are appended over time; the graph grows but stays sparse in typical tests.
// - Running Dijkstra from `node1` whenever `shortestPath` is called costs O((V + E) log V) with a
//   binary heap — simple, correct for nonnegative weights, no separate update logic when edges are added.
// - Alternative: maintain all-pairs shortest paths with Floyd–Warshall (O(n^3) setup, O(n^2) per
//   `addEdge` relaxation, O(1) query). Better only when n is small and queries vastly outnumber adds.
//
// Algorithm (Dijkstra)
// - Single-source shortest paths from `node1`: dist[x] = best known cost to reach x.
// - Min-heap ordered by tentative distance; pop smallest (lazy deletion when stale entries appear).
// - Relax outgoing edges (v, w) from u: if dist[u] + w < dist[v], update and push.
// - Stop early optional when node2 popped — implemented by checking when we extract node2 (first time
//   is optimal).
//
// Data structures
// - Adjacency list: `list[list[tuple[int,int]]]` — O(V + E) memory, fast iteration of out-edges.
// - `heapq` min-heap of `(distance, node)` pairs.
// - `dist` array length n, initialized to +infinity except source 0.
//
// Time complexity
// - `__init__`: O(n + |initial edges|).
// - `addEdge`: O(1) amortized append.
// - `shortestPath`: O((V + E') log V) where E' is edges present at query time (standard Dijkstra).
//
// Space complexity
// - O(V + E) for the graph plus O(V) for dist and O(E) heap worst-case — dominated by graph storage.
//
// Edge cases
// - node1 == node2 -> return 0 without searching.
// - Disconnected target -> heap empties, dist[node2] still inf -> -1.
// - Multiple edges u -> v: adjacency list keeps all; Dijkstra naturally picks cheapest combination.
//
// Improvements / variants
// - For tiny n and many queries: Floyd–Warshall incremental updates (see editorial).
// - For integer weights small: Dial’s algorithm (bucket deque) can replace heap.
// - Early exit: break when popped node == node2 (optional micro-optimization).
//
// LeetCode submission
// Put imports (`heapq`, `math`, `typing.List`) inside # @lc code=start.
//
// Interview walkthrough
// 1) Dynamic graph + shortest path queries -> incremental APSP vs on-demand SSSP.
// 2) Nonnegative weights -> Dijkstra; cite why not Bellman-Ford here.
// 3) Adjacency list + heap complexity.
// 4) Mention Floyd trade-off when interview asks for faster queries at small n.
// --- end notes ---
//
// @lc code=start

import "container/heap"

type _edge2642 struct {
	to int
	w  int
}

// Graph2642 is the LeetCode "Graph" object.
type Graph2642 struct {
	n int
	g [][]_edge2642
}

// Constructor2642 builds the initial directed graph.
func Constructor2642(n int, edges [][]int) Graph2642 {
	g := make([][]_edge2642, n)
	for _, e := range edges {
		u, v, w := e[0], e[1], e[2]
		g[u] = append(g[u], _edge2642{to: v, w: w})
	}
	return Graph2642{n: n, g: g}
}

// AddEdge appends another directed edge.
func (gr *Graph2642) AddEdge(edge []int) {
	u, v, w := edge[0], edge[1], edge[2]
	gr.g[u] = append(gr.g[u], _edge2642{to: v, w: w})
}

type _state2642 struct {
	d int64
	u int
}

type _pq2642 []_state2642

func (p _pq2642) Len() int            { return len(p) }
func (p _pq2642) Less(i, j int) bool  { return p[i].d < p[j].d }
func (p _pq2642) Swap(i, j int)       { p[i], p[j] = p[j], p[i] }
func (p *_pq2642) Push(x any)         { *p = append(*p, x.(_state2642)) }
func (p *_pq2642) Pop() any           { old := *p; x := old[len(old)-1]; *p = old[:len(old)-1]; return x }

// ShortestPath returns the minimum cost path from node1 to node2, or -1 if unreachable.
func (gr *Graph2642) ShortestPath(node1 int, node2 int) int {
	if node1 == node2 {
		return 0
	}
	const inf int64 = 1<<62
	dist := make([]int64, gr.n)
	for i := 0; i < gr.n; i++ {
		dist[i] = inf
	}
	dist[node1] = 0

	pq := &_pq2642{{d: 0, u: node1}}
	heap.Init(pq)

	for pq.Len() > 0 {
		cur := heap.Pop(pq).(_state2642)
		if cur.d != dist[cur.u] {
			continue
		}
		if cur.u == node2 {
			return int(cur.d)
		}
		for _, ed := range gr.g[cur.u] {
			nd := cur.d + int64(ed.w)
			if nd < dist[ed.to] {
				dist[ed.to] = nd
				heap.Push(pq, _state2642{d: nd, u: ed.to})
			}
		}
	}
	return -1
}

// @lc code=end

