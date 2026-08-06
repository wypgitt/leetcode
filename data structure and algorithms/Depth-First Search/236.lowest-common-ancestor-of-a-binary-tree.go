package leetcode

// LowestCommonAncestor236 recurses through a general binary tree. If p and q are
// found in different subtrees, the current root is their LCA; otherwise propagate
// the non-nil side upward.
//
// Time: O(n). Space: O(h).
func LowestCommonAncestor236(root, p, q *TreeNode) *TreeNode {
	if root == nil || root == p || root == q {
		return root
	}
	left := LowestCommonAncestor236(root.Left, p, q)
	right := LowestCommonAncestor236(root.Right, p, q)
	if left != nil && right != nil {
		return root
	}
	if left != nil {
		return left
	}
	return right
}
