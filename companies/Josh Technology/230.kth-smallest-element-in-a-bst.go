package leetcode

// KthSmallest230 iteratively performs inorder traversal with a stack. A BST's
// inorder order is sorted, so the kth popped node is the kth smallest value.
//
// Time: O(h+k). Space: O(h).
func KthSmallest230(root *TreeNode, k int) int {
	stack := []*TreeNode{}
	node := root
	for {
		for node != nil {
			stack = append(stack, node)
			node = node.Left
		}
		node = stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		k--
		if k == 0 {
			return node.Val
		}
		node = node.Right
	}
}
