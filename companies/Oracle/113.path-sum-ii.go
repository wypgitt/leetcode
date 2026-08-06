package leetcode

// PathSum113 backtracks over root-to-leaf paths. The path slice stores the
// current route and remaining target is reduced by each node. A valid path is
// copied only at a leaf with remaining sum zero.
//
// Time: O(n*h) worst case for copying valid paths. Space: O(h) excluding output.
func PathSum113(root *TreeNode, targetSum int) [][]int {
	ans := [][]int{}
	path := []int{}
	var dfs func(*TreeNode, int)
	dfs = func(node *TreeNode, remain int) {
		if node == nil {
			return
		}
		path = append(path, node.Val)
		remain -= node.Val
		if node.Left == nil && node.Right == nil && remain == 0 {
			ans = append(ans, append([]int(nil), path...))
		} else {
			dfs(node.Left, remain)
			dfs(node.Right, remain)
		}
		path = path[:len(path)-1]
	}
	dfs(root, targetSum)
	return ans
}
