package leetcode

//
// @lc app=leetcode id=3786 lang=golang
//
// [3786] Total Sum of Interaction Cost in Tree Groups
//
// Notes
// Count pair distances by edge contribution. Root the tree; for each child
// subtree, if it contains x nodes of group g and the whole tree has total[g],
// then x*(total[g]-x) same-group paths cross the parent edge. Group labels are
// limited to 20, so fixed [21]int arrays are faster and simpler than maps.
// Time: O(20n). Space: O(20n).
//
// @lc code=start

func InteractionCosts3786(n int, edges [][]int, group []int) int {
	if n == 1 {
		return 0
	}

	adjacency := make([][]int, n)
	for _, edge := range edges {
		a, b := edge[0], edge[1]
		adjacency[a] = append(adjacency[a], b)
		adjacency[b] = append(adjacency[b], a)
	}

	total := [21]int{}
	for _, label := range group {
		total[label]++
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

	subtreeCounts := make([][21]int, n)
	answer := 0
	for i := len(order) - 1; i >= 0; i-- {
		node := order[i]
		counts := &subtreeCounts[node]
		counts[group[node]]++

		if node != 0 {
			for label := 1; label <= 20; label++ {
				inside := counts[label]
				answer += inside * (total[label] - inside)
			}

			parentCounts := &subtreeCounts[parent[node]]
			for label := 1; label <= 20; label++ {
				parentCounts[label] += counts[label]
			}
		}
	}

	return answer
}

// @lc code=end
