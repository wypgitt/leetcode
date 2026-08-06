package leetcode

// BuildTree106 reconstructs a tree from inorder and postorder traversals.
// Postorder gives each subtree root last; the inorder index splits left and
// right subtree ranges.
//
// Time: O(n). Space: O(n).
func BuildTree106(inorder []int, postorder []int) *TreeNode {
	idx := map[int]int{}
	for i, v := range inorder {
		idx[v] = i
	}
	var build func(int, int, int, int) *TreeNode
	build = func(inL, inR, postL, postR int) *TreeNode {
		if inL > inR {
			return nil
		}
		rootVal := postorder[postR]
		mid := idx[rootVal]
		leftSize := mid - inL
		root := &TreeNode{Val: rootVal}
		root.Left = build(inL, mid-1, postL, postL+leftSize-1)
		root.Right = build(mid+1, inR, postL+leftSize, postR-1)
		return root
	}
	return build(0, len(inorder)-1, 0, len(postorder)-1)
}
