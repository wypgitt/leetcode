package leetcode

// UpsideDownBinaryTree156 walks down the left spine while rewiring pointers. The
// previous parent becomes the new right child, and the previous right sibling
// becomes the new left child.
//
// Time: O(h). Space: O(1).
func UpsideDownBinaryTree156(root *TreeNode) *TreeNode {
	var parent, parentRight *TreeNode
	cur := root
	for cur != nil {
		nextLeft := cur.Left
		cur.Left = parentRight
		parentRight = cur.Right
		cur.Right = parent
		parent = cur
		cur = nextLeft
	}
	return parent
}
