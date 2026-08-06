package leetcode

//
// @lc app=leetcode id=3772 lang=golang
//
// [3772] Maximum Subgraph Score in a Tree
//
// Notes
// Convert good nodes to +1 and bad nodes to -1. First compute down[u], the best
// connected contribution inside u's rooted subtree, keeping only positive child
// contributions. Then reroot: each child receives its own down value plus any
// positive contribution from the rest of the tree. Iterative traversal avoids
// recursion-depth issues. Time: O(n). Space: O(n).
//
// @lc code=start

func MaxSubgraphScore3772(n int, edges [][]int, good []int) []int {
	adjacency := make([][]int, n)
	for _, edge := range edges {
		a, b := edge[0], edge[1]
		adjacency[a] = append(adjacency[a], b)
		adjacency[b] = append(adjacency[b], a)
	}

	weight := make([]int, n)
	for i, value := range good {
		if value == 1 {
			weight[i] = 1
		} else {
			weight[i] = -1
		}
	}

	parent := make([]int, n)
	for i := range parent {
		parent[i] = -1
	}
	order := []int{0}
	for idx := 0; idx < len(order); idx++ {
		node := order[idx]
		for _, neighbor := range adjacency[node] {
			if neighbor == parent[node] {
				continue
			}
			parent[neighbor] = node
			order = append(order, neighbor)
		}
	}

	down := append([]int(nil), weight...)
	for i := len(order) - 1; i >= 0; i-- {
		node := order[i]
		for _, neighbor := range adjacency[node] {
			if parent[neighbor] == node && down[neighbor] > 0 {
				down[node] += down[neighbor]
			}
		}
	}

	answer := make([]int, n)
	answer[0] = down[0]
	for _, node := range order {
		for _, neighbor := range adjacency[node] {
			if parent[neighbor] != node {
				continue
			}
			withoutChild := answer[node]
			if down[neighbor] > 0 {
				withoutChild -= down[neighbor]
			}
			answer[neighbor] = down[neighbor]
			if withoutChild > 0 {
				answer[neighbor] += withoutChild
			}
		}
	}

	return answer
}

// @lc code=end
