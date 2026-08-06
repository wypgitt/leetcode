package leetcode

// SortedListToBST109 counts the linked list length, then simulates inorder tree
// construction. Build the left subtree, consume the current list node as root,
// then build the right subtree. This uses the sorted list in one forward pass.
//
// Time: O(n). Space: O(log n) recursion for the balanced output tree.
func SortedListToBST109(head *ListNode) *TreeNode {
	length := 0
	for cur := head; cur != nil; cur = cur.Next {
		length++
	}
	current := head
	var build func(int) *TreeNode
	build = func(size int) *TreeNode {
		if size <= 0 {
			return nil
		}
		left := build(size / 2)
		root := &TreeNode{Val: current.Val, Left: left}
		current = current.Next
		root.Right = build(size - size/2 - 1)
		return root
	}
	return build(length)
}
