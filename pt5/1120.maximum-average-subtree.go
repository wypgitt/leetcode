package main

type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}

func maximumAverageSubtree(root *TreeNode) float64 {
	best := 0.0

	var dfs func(*TreeNode) (int, int)
	dfs = func(node *TreeNode) (int, int) {
		if node == nil {
			return 0, 0
		}

		leftSum, leftCount := dfs(node.Left)
		rightSum, rightCount := dfs(node.Right)
		totalSum := leftSum + rightSum + node.Val
		totalCount := leftCount + rightCount + 1
		average := float64(totalSum) / float64(totalCount)
		if average > best {
			best = average
		}
		return totalSum, totalCount
	}

	dfs(root)
	return best
}

