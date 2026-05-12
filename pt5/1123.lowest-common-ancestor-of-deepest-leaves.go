package main

type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}

func lcaDeepestLeaves(root *TreeNode) *TreeNode {
	var dfs func(*TreeNode) (int, *TreeNode)
	dfs = func(node *TreeNode) (int, *TreeNode) {
		if node == nil {
			return 0, nil
		}

		leftDepth, leftLCA := dfs(node.Left)
		rightDepth, rightLCA := dfs(node.Right)
		if leftDepth == rightDepth {
			return leftDepth + 1, node
		}
		if leftDepth > rightDepth {
			return leftDepth + 1, leftLCA
		}
		return rightDepth + 1, rightLCA
	}

	_, answer := dfs(root)
	return answer
}

