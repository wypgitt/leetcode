package leetcode

//
// LeetCode 156 — Binary Tree Upside Down
//
// Problem (one level):
//   Given a node with left child L and right child R, “flip” this triangle so that
//   L becomes the new root, R becomes L’s new left child, and the old root becomes
//   L’s new right child.
//
// Why iteration along the left spine works:
//   The guarantee (every right node has a left sibling and no children) means the
//   tree is effectively a chain along the left edge with optional right “buds”.
//   Processing from the original root downward is the same as flipping level by
//   level from top to bottom; each step only needs the previous parent and that
//   parent’s old right child to wire the new left/right pointers.
//
// Variables:
//   curr          — node we are rewiring this iteration (walking left).
//   parent        — the node that was above curr in the original tree; becomes
//                   curr’s new right child after the flip at this step.
//   parent_right  — the old right child of `parent` (sibling of curr in the
//                   original tree); becomes curr’s new left child. For the first
//                   node we process, there is no such sibling yet, so None.

// UpsideDownBinaryTree156 flips the tree upside down as described in the problem.
func UpsideDownBinaryTree156(root *TreeNode) *TreeNode {
	curr := root
	var parent *TreeNode
	var parentRight *TreeNode

	for curr != nil {
		// Save children before we overwrite pointers.
		left := curr.Left
		right := curr.Right

		// Apply the upside-down rule for this node:
		// new left  = old right sibling of the node above (nil on first step)
		// new right = old parent
		curr.Left = parentRight
		curr.Right = parent

		// Advance: next node down the left spine; carry flip context upward.
		parentRight = right
		parent = curr
		curr = left
	}

	// Last processed node was the old leftmost node — it is the new root.
	return parent
}

