package leetcode

// Connect117 handles an arbitrary binary tree by walking the current level via
// existing next pointers while building the next level with dummy and tail
// pointers. This gives BFS-like linking without a queue.
//
// Time: O(n). Space: O(1).
func Connect117(root *Node) *Node {
	current := root
	for current != nil {
		dummy := &Node{}
		tail := dummy
		for current != nil {
			if current.Left != nil {
				tail.Next = current.Left
				tail = tail.Next
			}
			if current.Right != nil {
				tail.Next = current.Right
				tail = tail.Next
			}
			current = current.Next
		}
		current = dummy.Next
	}
	return root
}
