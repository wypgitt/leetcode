package leetcode

// EventualSafeNodes802 uses DFS colors: 0 unvisited, 1 visiting, 2 safe. A gray
// revisit means a cycle; a node becomes safe only if all outgoing neighbors are
// safe.
//
// Time: O(V+E). Space: O(V).
func EventualSafeNodes802(graph [][]int) []int {
	n := len(graph)
	color := make([]int, n)
	var dfs func(int) bool
	dfs = func(node int) bool {
		if color[node] != 0 {
			return color[node] == 2
		}
		color[node] = 1
		for _, nei := range graph[node] {
			if !dfs(nei) {
				return false
			}
		}
		color[node] = 2
		return true
	}
	ans := []int{}
	for i := 0; i < n; i++ {
		if dfs(i) {
			ans = append(ans, i)
		}
	}
	return ans
}
