package main

type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}

type FindElements struct {
	values map[int]bool
}

func Constructor(root *TreeNode) FindElements {
	f := FindElements{values: map[int]bool{}}
	var recover func(*TreeNode, int)
	recover = func(node *TreeNode, value int) {
		if node == nil {
			return
		}
		node.Val = value
		f.values[value] = true
		recover(node.Left, 2*value+1)
		recover(node.Right, 2*value+2)
	}
	recover(root, 0)
	return f
}

func (f *FindElements) Find(target int) bool {
	return f.values[target]
}

/*
Explanation

Recovery is deterministic: root is 0, a left child is 2*x+1, and a right child
is 2*x+2. DFS the tree once in the constructor, assign recovered values, and
store every value in a map set.

The map makes Find O(1) average time. Without it, each query would need a tree
walk or path reconstruction.

Edge cases: missing children are skipped; a single root recovers to value 0;
targets larger than any recovered value return false.

Time complexity: constructor O(n), Find O(1) average.
Space complexity: O(n).
*/
