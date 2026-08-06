package leetcode

// RightSideView199 performs level-order traversal and records the last node seen
// at each level, which is the visible node from the right side.
//
// Time: O(n). Space: O(w).
func RightSideView199(root *TreeNode) []int {
	if root == nil {
		return []int{}
	}
	ans := []int{}
	q := []*TreeNode{root}
	for len(q) > 0 {
		size := len(q)
		for i := 0; i < size; i++ {
			node := q[0]
			q = q[1:]
			if i == size-1 {
				ans = append(ans, node.Val)
			}
			if node.Left != nil {
				q = append(q, node.Left)
			}
			if node.Right != nil {
				q = append(q, node.Right)
			}
		}
	}
	return ans
}
