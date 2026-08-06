package leetcode

// FindClosestLeaf742 converts the tree to an undirected graph through parent
// links, then BFSes from the target node. The first leaf dequeued is closest by
// edge count and can be below the target or through an ancestor.
//
// Go data structure note: map[*TreeNode][]*TreeNode uses node pointers as graph
// keys, matching object identity from the original tree.
//
// Time: O(n). Space: O(n).
func FindClosestLeaf742(root *TreeNode, k int) int {
	graph := map[*TreeNode][]*TreeNode{}
	var target *TreeNode
	var build func(*TreeNode, *TreeNode)
	build = func(node, parent *TreeNode) {
		if node == nil {
			return
		}
		if node.Val == k {
			target = node
		}
		if parent != nil {
			graph[node] = append(graph[node], parent)
			graph[parent] = append(graph[parent], node)
		}
		build(node.Left, node)
		build(node.Right, node)
	}
	build(root, nil)
	queue := []*TreeNode{target}
	seen := map[*TreeNode]bool{target: true}
	for head := 0; head < len(queue); head++ {
		node := queue[head]
		if node.Left == nil && node.Right == nil {
			return node.Val
		}
		for _, nei := range graph[node] {
			if !seen[nei] {
				seen[nei] = true
				queue = append(queue, nei)
			}
		}
	}
	return root.Val
}
