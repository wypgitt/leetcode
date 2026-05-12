package main

type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}

func btreeGameWinningMove(root *TreeNode, n int, x int) bool {
	leftSize, rightSize := 0, 0

	var size func(*TreeNode) int
	size = func(node *TreeNode) int {
		if node == nil {
			return 0
		}
		left := size(node.Left)
		right := size(node.Right)
		if node.Val == x {
			leftSize = left
			rightSize = right
		}
		return left + right + 1
	}

	size(root)
	parentSide := n - leftSize - rightSize - 1
	largest := leftSize
	if rightSize > largest {
		largest = rightSize
	}
	if parentSide > largest {
		largest = parentSide
	}
	return largest > n/2
}

