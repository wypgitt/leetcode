package leetcode

// GenerateTrees95 recursively chooses each value as root, combines every left
// subtree with every right subtree, and memoizes ranges. Empty subtrees are
// represented by a single nil option so leaf combinations work.
//
// Time/space: O(Cn*n) for Cn generated trees.
func GenerateTrees95(n int) []*TreeNode {
	type key struct{ lo, hi int }
	memo := map[key][]*TreeNode{}
	var build func(int, int) []*TreeNode
	build = func(lo, hi int) []*TreeNode {
		if lo > hi {
			return []*TreeNode{nil}
		}
		k := key{lo, hi}
		if v, ok := memo[k]; ok {
			return v
		}
		trees := []*TreeNode{}
		for rootVal := lo; rootVal <= hi; rootVal++ {
			for _, left := range build(lo, rootVal-1) {
				for _, right := range build(rootVal+1, hi) {
					root := &TreeNode{Val: rootVal, Left: left, Right: right}
					trees = append(trees, root)
				}
			}
		}
		memo[k] = trees
		return trees
	}
	return build(1, n)
}
