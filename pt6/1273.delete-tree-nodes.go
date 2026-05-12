package main

func deleteTreeNodes(nodes int, parent []int, value []int) int {
	children := make([][]int, nodes)
	root := 0
	for node, par := range parent {
		if par == -1 {
			root = node
		} else {
			children[par] = append(children[par], node)
		}
	}

	var dfs func(int) (int, int)
	dfs = func(node int) (int, int) {
		sum, count := value[node], 1
		for _, child := range children[node] {
			childSum, childCount := dfs(child)
			sum += childSum
			count += childCount
		}
		if sum == 0 {
			return 0, 0
		}
		return sum, count
	}

	_, remaining := dfs(root)
	return remaining
}

/*
Explanation

Build children lists from the parent array. A postorder DFS returns two values
for each subtree: its sum and how many nodes remain after deletions. If the
subtree sum is zero, the entire subtree is deleted and contributes count 0 to
its parent.

Postorder is required because a node's fate depends on every descendant's
value. A slice of child slices is the natural Go representation when node ids
are 0..nodes-1.

Edge cases: the root can be deleted; nested zero-sum subtrees; negative values
are handled by normal addition.

Time complexity: O(n).
Space complexity: O(n).
*/
