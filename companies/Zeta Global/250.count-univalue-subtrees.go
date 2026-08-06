package leetcode

// CountUnivalSubtrees250 postorder-checks whether each subtree is univalue. A
// subtree is counted when both children are univalue and any existing child has
// the same value as the current node.
//
// Time: O(n). Space: O(h).
func CountUnivalSubtrees250(root *TreeNode) int {
	count := 0
	var dfs func(*TreeNode) bool
	dfs = func(node *TreeNode) bool {
		if node == nil {
			return true
		}
		left, right := dfs(node.Left), dfs(node.Right)
		if !left || !right {
			return false
		}
		if node.Left != nil && node.Left.Val != node.Val {
			return false
		}
		if node.Right != nil && node.Right.Val != node.Val {
			return false
		}
		count++
		return true
	}
	dfs(root)
	return count
}
