package leetcode

// IsValidBST98 passes exclusive inherited lower and upper bounds. This catches
// violations deep in a subtree, not just parent-child violations. nil subtrees
// are valid.
//
// Time: O(n). Space: O(h).
func IsValidBST98(root *TreeNode) bool {
	var dfs func(*TreeNode, *int, *int) bool
	dfs = func(node *TreeNode, low, high *int) bool {
		if node == nil {
			return true
		}
		if low != nil && node.Val <= *low {
			return false
		}
		if high != nil && node.Val >= *high {
			return false
		}
		return dfs(node.Left, low, &node.Val) && dfs(node.Right, &node.Val, high)
	}
	return dfs(root, nil, nil)
}
