package leetcode

// LevelOrderBottom107 collects normal BFS levels, then reverses the level slice
// so the output is bottom-up. Each BFS pass consumes exactly the current queue
// length, preserving depth groups.
//
// Time: O(n). Space: O(w) plus output.
func LevelOrderBottom107(root *TreeNode) [][]int {
	levels := LevelOrder102(root)
	for l, r := 0, len(levels)-1; l < r; l, r = l+1, r-1 {
		levels[l], levels[r] = levels[r], levels[l]
	}
	return levels
}
