package leetcode

// LevelOrder102 is breadth-first search. A slice with a moving head index acts
// as a FIFO queue; each outer loop consumes the current queue size to form one
// depth level.
//
// Time: O(n). Space: O(w), maximum tree width.
func LevelOrder102(root *TreeNode) [][]int {
	if root == nil {
		return [][]int{}
	}
	ans := [][]int{}
	q := []*TreeNode{root}
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
		ans = append(ans, level)
	}
	return ans
}
