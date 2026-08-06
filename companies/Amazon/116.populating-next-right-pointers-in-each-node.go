package leetcode

// Connect116 exploits the perfect-tree invariant. Existing next pointers let us
// walk a level; for each node, connect left->right and right->node.next.left for
// cross-parent links.
//
// Time: O(n). Space: O(1).
func Connect116(root *Node) *Node {
	leftmost := root
	for leftmost != nil && leftmost.Left != nil {
		for node := leftmost; node != nil; node = node.Next {
			node.Left.Next = node.Right
			if node.Next != nil {
				node.Right.Next = node.Next.Left
			}
		}
		leftmost = leftmost.Left
	}
	return root
}
