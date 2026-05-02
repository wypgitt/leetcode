package leetcode

// LeetCode 156. Binary Tree Upside Down
// https://leetcode.com/problems/binary-tree-upside-down/

// @lc code=start

// UpsideDownBinaryTreeBinaryTreeFile flips the binary tree upside down (same problem as 156; distinct name for this filename in package leetcode).
func UpsideDownBinaryTreeBinaryTreeFile(root *TreeNode) *TreeNode {
	curr := root
	var parent *TreeNode
	var parentRight *TreeNode // old right sibling of `parent` → becomes new left child

	for curr != nil {
		left := curr.Left
		right := curr.Right

		curr.Left = parentRight
		curr.Right = parent

		parentRight = right
		parent = curr
		curr = left
	}
	return parent
}

// @lc code=end

