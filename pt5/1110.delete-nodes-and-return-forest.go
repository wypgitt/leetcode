package main

type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}

func delNodes(root *TreeNode, toDelete []int) []*TreeNode {
	deleted := map[int]bool{}
	for _, value := range toDelete {
		deleted[value] = true
	}

	forest := []*TreeNode{}
	var prune func(*TreeNode, bool) *TreeNode
	prune = func(node *TreeNode, isRoot bool) *TreeNode {
		if node == nil {
			return nil
		}

		isDeleted := deleted[node.Val]
		if isRoot && !isDeleted {
			forest = append(forest, node)
		}

		node.Left = prune(node.Left, isDeleted)
		node.Right = prune(node.Right, isDeleted)
		if isDeleted {
			return nil
		}
		return node
	}

	prune(root, true)
	return forest
}

