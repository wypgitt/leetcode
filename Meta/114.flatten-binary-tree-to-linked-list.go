package leetcode

// Flatten114 processes reverse preorder (right, left, root). prev is the head of
// the already-flattened suffix; each node points right to prev and left to nil,
// producing the required preorder right chain in place.
//
// Time: O(n). Space: O(h).
func Flatten114(root *TreeNode) {
	var prev *TreeNode
	var dfs func(*TreeNode)
	dfs = func(node *TreeNode) {
		if node == nil {
			return
		}
		dfs(node.Right)
		dfs(node.Left)
		node.Right = prev
		node.Left = nil
		prev = node
	}
	dfs(root)
}
