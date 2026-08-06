package leetcode

// RecoverTree99 finds inversions in the inorder traversal of a BST. The first
// misplaced node is prev in the first inversion; the second is the current node
// in the last inversion. Swapping their values restores the tree structure.
//
// Time: O(n). Space: O(h).
func RecoverTree99(root *TreeNode) {
	var first, second, prev *TreeNode
	var inorder func(*TreeNode)
	inorder = func(node *TreeNode) {
		if node == nil {
			return
		}
		inorder(node.Left)
		if prev != nil && prev.Val > node.Val {
			if first == nil {
				first = prev
			}
			second = node
		}
		prev = node
		inorder(node.Right)
	}
	inorder(root)
	if first != nil && second != nil {
		first.Val, second.Val = second.Val, first.Val
	}
}
