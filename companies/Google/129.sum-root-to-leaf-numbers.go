package leetcode

// SumNumbers129 carries the numeric prefix down the tree. Visiting child digit d
// updates current to current*10+d; a leaf contributes that complete number.
//
// Time: O(n). Space: O(h) recursion.
func SumNumbers129(root *TreeNode) int {
	var dfs func(*TreeNode, int) int
	dfs = func(node *TreeNode, cur int) int {
		if node == nil {
			return 0
		}
		cur = cur*10 + node.Val
		if node.Left == nil && node.Right == nil {
			return cur
		}
		return dfs(node.Left, cur) + dfs(node.Right, cur)
	}
	return dfs(root, 0)
}
