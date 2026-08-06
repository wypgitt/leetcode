package leetcode

// CheckEqualTree663 computes every subtree sum with postorder DFS. Cutting one
// edge can split the tree equally exactly when a non-root subtree has sum
// total/2; the root sum is excluded because cutting above the root is invalid.
//
// Time: O(n). Space: O(n).
func CheckEqualTree663(root *TreeNode) bool {
	sums := []int{}
	var dfs func(*TreeNode) int
	dfs = func(node *TreeNode) int {
		if node == nil {
			return 0
		}
		total := node.Val + dfs(node.Left) + dfs(node.Right)
		sums = append(sums, total)
		return total
	}
	total := dfs(root)
	if len(sums) > 0 {
		sums = sums[:len(sums)-1]
	}
	if total%2 != 0 {
		return false
	}
	for _, s := range sums {
		if s == total/2 {
			return true
		}
	}
	return false
}
