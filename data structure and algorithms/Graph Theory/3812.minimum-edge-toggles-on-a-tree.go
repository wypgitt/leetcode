package leetcode

//
// @lc app=leetcode id=3812 lang=golang
//
// [3812] Minimum Edge Toggles on a Tree
//
// Notes
// Interpret start/target mismatches as node parity needs. Root the tree and
// process leaves upward; if a child still needs a flip, toggle its parent edge,
// which fixes the child and flips the parent's need. The root must end even.
// Returned edge ids are sorted to match the Python implementation. Time: O(n log
// n) for sorting the answer. Space: O(n).
//
// @lc code=start

import "sort"

type edge3812 struct {
	to  int
	idx int
}

func MinimumFlips3812(n int, edges [][]int, start string, target string) []int {
	graph := make([][]edge3812, n)
	for idx, edge := range edges {
		u, v := edge[0], edge[1]
		graph[u] = append(graph[u], edge3812{to: v, idx: idx})
		graph[v] = append(graph[v], edge3812{to: u, idx: idx})
	}

	parent := make([]int, n)
	parentEdge := make([]int, n)
	for i := 0; i < n; i++ {
		parent[i] = -1
		parentEdge[i] = -1
	}

	order := []int{0}
	for idx := 0; idx < len(order); idx++ {
		node := order[idx]
		for _, edge := range graph[node] {
			if edge.to == parent[node] {
				continue
			}
			parent[edge.to] = node
			parentEdge[edge.to] = edge.idx
			order = append(order, edge.to)
		}
	}

	need := make([]int, n)
	for i := 0; i < n; i++ {
		if start[i] != target[i] {
			need[i] = 1
		}
	}

	answer := []int{}
	for i := len(order) - 1; i >= 1; i-- {
		node := order[i]
		if need[node] == 1 {
			answer = append(answer, parentEdge[node])
			need[node] ^= 1
			need[parent[node]] ^= 1
		}
	}

	if need[0] == 1 {
		return []int{-1}
	}
	sort.Ints(answer)
	return answer
}

// @lc code=end
