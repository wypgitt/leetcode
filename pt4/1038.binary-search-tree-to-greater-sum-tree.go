package main

/*
1038. Binary Search Tree to Greater Sum Tree

LeetCode provides:
type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}
*/
func bstToGst(root *TreeNode) *TreeNode {
	runningSum := 0

	var reverseInorder func(node *TreeNode)
	reverseInorder = func(node *TreeNode) {
		if node == nil {
			return
		}

		reverseInorder(node.Right)
		runningSum += node.Val
		node.Val = runningSum
		reverseInorder(node.Left)
	}

	reverseInorder(root)
	return root
}

/*
Interview Explanation

Core idea:
A normal inorder traversal of a BST visits values in ascending order. Reverse
inorder visits values in descending order, so when processing a node we have
already accumulated every greater value.

Go data structures:
- The TreeNode pointers define the BST.
- A recursive closure performs reverse inorder traversal.
- runningSum is captured by the closure and shared across recursive calls.

Algorithm:
1. Traverse the right subtree.
2. Add the current node's original value to runningSum.
3. Replace node.Val with runningSum.
4. Traverse the left subtree.

Correctness:
When a node is visited in reverse inorder, all greater BST values have already
been added to runningSum and no smaller values have been added. After adding
the current value, runningSum equals current value plus all greater values,
which is exactly the Greater Sum Tree value.

Complexity:
Each node is visited once: O(n) time. Recursion uses O(h) stack space, where h
is tree height.

Edge cases:
- Single-node tree stays the same.
- Left- or right-skewed trees still follow BST sorted order.
- Value 0 contributes normally.
*/
