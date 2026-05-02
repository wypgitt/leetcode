// Shared LeetCode-style definitions used by multiple translated solutions in this repo.
// Keeping one definition avoids duplicate type declarations in the same package.

package leetcode

// TreeNode is the classic binary tree node used across tree problems.
type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}

// ListNode is the classic singly-linked list node used across linked-list problems.
type ListNode struct {
	Val  int
	Next *ListNode
}
