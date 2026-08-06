package leetcode

// ZigzagLevelOrder103 performs normal BFS to preserve level grouping, then
// reverses values on alternating levels. The queue invariant stays standard BFS.
//
// Time: O(n). Space: O(w).
func ZigzagLevelOrder103(root *TreeNode) [][]int {
	if root == nil {
		return [][]int{}
	}
	ans := [][]int{}
	q := []*TreeNode{root}
	leftToRight := true
	for len(q) > 0 {
		size := len(q)
		level := make([]int, 0, size)
		for i := 0; i < size; i++ {
			node := q[0]
			q = q[1:]
			level = append(level, node.Val)
			if node.Left != nil {
				q = append(q, node.Left)
			}
			if node.Right != nil {
				q = append(q, node.Right)
			}
		}
		if !leftToRight {
			for l, r := 0, len(level)-1; l < r; l, r = l+1, r-1 {
				level[l], level[r] = level[r], level[l]
			}
		}
		ans = append(ans, level)
		leftToRight = !leftToRight
	}
	return ans
}
