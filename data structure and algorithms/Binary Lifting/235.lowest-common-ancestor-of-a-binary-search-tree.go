package leetcode

// LowestCommonAncestor235 uses BST ordering. If both target values are below the
// current node, go left; if both are above, go right; otherwise the current node
// splits the paths and is the LCA.
//
// Time: O(h). Space: O(1).
func LowestCommonAncestor235(root, p, q *TreeNode) *TreeNode {
	low, high := p.Val, q.Val
	if low > high {
		low, high = high, low
	}
	node := root
	for node != nil {
		if high < node.Val {
			node = node.Left
		} else if low > node.Val {
			node = node.Right
		} else {
			return node
		}
	}
	return nil
}
