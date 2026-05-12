package main

type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}

func twoSumBSTs(root1 *TreeNode, root2 *TreeNode, target int) bool {
	values := map[int]struct{}{}

	var collect func(*TreeNode)
	collect = func(node *TreeNode) {
		if node == nil {
			return
		}
		values[node.Val] = struct{}{}
		collect(node.Left)
		collect(node.Right)
	}

	var search func(*TreeNode) bool
	search = func(node *TreeNode) bool {
		if node == nil {
			return false
		}
		if _, ok := values[target-node.Val]; ok {
			return true
		}
		return search(node.Left) || search(node.Right)
	}

	collect(root1)
	return search(root2)
}

/*
Explanation

Traverse the first BST and put every value into a hash set. Then traverse the
second BST and check whether target-node.Val exists in that set.

The BST ordering is not required because the question only asks whether a pair
exists. A hash set gives average O(1) complement lookup and keeps the interview
explanation simple. A two-iterator sorted traversal is another option, but it
is more code for the same asymptotic time with less extra memory.

Go data structure: map[int]struct{} is the idiomatic set when only membership
matters. struct{} takes no storage for a value payload.

Edge cases: one tree can be nil; duplicate values do not matter because the two
numbers always come from different trees; negative values work with the same
complement formula.

Time complexity: O(n + m).
Space complexity: O(n) for values from root1 plus recursion stack.
*/
