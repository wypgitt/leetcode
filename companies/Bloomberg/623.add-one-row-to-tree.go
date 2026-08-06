package leetcode

// AddOneRow623 BFSes to depth-1, then inserts a new left and right node under
// each node at that level. Old left and right subtrees are attached under the
// new nodes according to the problem rule.
//
// Time: O(n) worst case. Space: O(w) for the BFS frontier.
func AddOneRow623(root *TreeNode, val int, depth int) *TreeNode {
	if depth == 1 {
		return &TreeNode{Val: val, Left: root}
	}
	queue := []*TreeNode{root}
	currentDepth := 1
	for len(queue) > 0 && currentDepth < depth-1 {
		size := len(queue)
		for i := 0; i < size; i++ {
			node := queue[0]
			queue = queue[1:]
			if node.Left != nil {
				queue = append(queue, node.Left)
			}
			if node.Right != nil {
				queue = append(queue, node.Right)
			}
		}
		currentDepth++
	}
	for _, node := range queue {
		oldLeft, oldRight := node.Left, node.Right
		node.Left = &TreeNode{Val: val, Left: oldLeft}
		node.Right = &TreeNode{Val: val, Right: oldRight}
	}
	return root
}
