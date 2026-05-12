package main

/*
1026. Maximum Difference Between Node and Ancestor

LeetCode provides:
type TreeNode struct {
	Val   int
	Left  *TreeNode
	Right *TreeNode
}
*/
func maxAncestorDiff(root *TreeNode) int {
	var dfs func(node *TreeNode, pathMin, pathMax int) int
	dfs = func(node *TreeNode, pathMin, pathMax int) int {
		if node == nil {
			return pathMax - pathMin
		}

		if node.Val < pathMin {
			pathMin = node.Val
		}
		if node.Val > pathMax {
			pathMax = node.Val
		}

		left := dfs(node.Left, pathMin, pathMax)
		right := dfs(node.Right, pathMin, pathMax)
		if left > right {
			return left
		}
		return right
	}

	return dfs(root, root.Val, root.Val)
}

/*
Interview Explanation

Core idea:
For a node, the best difference with any ancestor only depends on the minimum
and maximum values seen on the root-to-node path. We do not need the full list
of ancestors.

Go data structures:
- The recursion stack represents the current tree path.
- Two ints, pathMin and pathMax, summarize all ancestor values needed for the
  answer.

Algorithm:
1. DFS from root.
2. At each node, update pathMin and pathMax with node.Val.
3. At a nil child, return pathMax - pathMin for that completed path.
4. Return the larger result from left and right subtrees.

Correctness:
Every ancestor-descendant pair appears on a root-to-node path. The maximum
absolute difference among values on that path is max minus min. DFS evaluates
that quantity for every path, so the maximum returned is the best valid
ancestor difference.

Complexity:
Each node is visited once, giving O(n) time. The call stack uses O(h) space,
where h is tree height.

Edge cases:
- Skewed trees work because min and max flow down the path.
- The root can be either the min or the max.
- The constraints guarantee root is non-nil.
*/
