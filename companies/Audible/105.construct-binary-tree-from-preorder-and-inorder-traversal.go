package leetcode

// BuildTree105 reconstructs a tree from preorder and inorder traversals.
// Preorder gives each subtree root first; an inorder value->index map gives the
// left subtree size in O(1), so each node is created once.
//
// Time: O(n). Space: O(n) for map plus recursion.
func BuildTree105(preorder []int, inorder []int) *TreeNode {
	idx := map[int]int{}
	for i, v := range inorder {
		idx[v] = i
	}
	var build func(int, int, int, int) *TreeNode
	build = func(preL, preR, inL, inR int) *TreeNode {
		if preL > preR {
			return nil
		}
		rootVal := preorder[preL]
		mid := idx[rootVal]
		leftSize := mid - inL
		root := &TreeNode{Val: rootVal}
		root.Left = build(preL+1, preL+leftSize, inL, mid-1)
		root.Right = build(preL+leftSize+1, preR, mid+1, inR)
		return root
	}
	return build(0, len(preorder)-1, 0, len(inorder)-1)
}
