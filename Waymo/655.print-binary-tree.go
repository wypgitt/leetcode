package leetcode

// PrintTree655 creates h rows and 2^h-1 columns, then places each node at the
// midpoint of its assigned column range. Children receive the left and right
// halves of that range.
//
// Time: O(n + h*2^h) including grid initialization. Space: O(h*2^h).
func PrintTree655(root *TreeNode) [][]string {
	var height func(*TreeNode) int
	height = func(node *TreeNode) int {
		if node == nil {
			return 0
		}
		return 1 + maxInt(height(node.Left), height(node.Right))
	}
	h := height(root)
	cols := (1 << h) - 1
	ans := make([][]string, h)
	for i := range ans {
		ans[i] = make([]string, cols)
	}
	var place func(*TreeNode, int, int, int)
	place = func(node *TreeNode, r, lo, hi int) {
		if node == nil {
			return
		}
		mid := (lo + hi) / 2
		ans[r][mid] = intToString(node.Val)
		place(node.Left, r+1, lo, mid-1)
		place(node.Right, r+1, mid+1, hi)
	}
	place(root, 0, 0, cols-1)
	return ans
}
