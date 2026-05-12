package main

type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}

func maxLevelSum(root *TreeNode) int {
	queue := []*TreeNode{root}
	bestSum := -1 << 60
	bestLevel, level := 1, 1

	for len(queue) > 0 {
		levelSize := len(queue)
		levelSum := 0
		for i := 0; i < levelSize; i++ {
			node := queue[0]
			queue = queue[1:]
			levelSum += node.Val
			if node.Left != nil {
				queue = append(queue, node.Left)
			}
			if node.Right != nil {
				queue = append(queue, node.Right)
			}
		}
		if levelSum > bestSum {
			bestSum = levelSum
			bestLevel = level
		}
		level++
	}

	return bestLevel
}

