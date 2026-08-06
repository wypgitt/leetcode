package leetcode

// ListNode is the standard LeetCode singly linked-list node.
type ListNode struct {
	Val  int
	Next *ListNode
}

// TreeNode is the standard LeetCode binary-tree node.
type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}

func absInt(x int) int {
	if x < 0 {
		return -x
	}
	return x
}
func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}
func maxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}
