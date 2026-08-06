package leetcode

//
// @lc app=leetcode id=3879 lang=golang
//
// [3879] Maximum Distinct Path Sum in a Binary Tree
//
// Notes
// Convert the tree to an undirected graph indexed by node pointer, then start a
// DFS from every node. The DFS carries a set of values already on the path and
// refuses to extend through duplicates, updating the best path sum seen. Go maps
// keyed by *TreeNode and int replace Python dict/set. Time: O(n^2) worst case.
// Space: O(n).
//
// @lc code=start

func MaxSum3879(root *TreeNode) int {
	if root == nil {
		return 0
	}

	nodeToIndex := map[*TreeNode]int{}
	values := []int{}
	graph := [][]int{}

	addNode := func(node *TreeNode) int {
		if index, ok := nodeToIndex[node]; ok {
			return index
		}
		index := len(values)
		nodeToIndex[node] = index
		values = append(values, node.Val)
		graph = append(graph, []int{})
		return index
	}

	stack := []*TreeNode{root}
	for len(stack) > 0 {
		node := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		if node == nil {
			continue
		}

		index := addNode(node)
		if node.Left != nil {
			leftIndex := addNode(node.Left)
			graph[index] = append(graph[index], leftIndex)
			graph[leftIndex] = append(graph[leftIndex], index)
			stack = append(stack, node.Left)
		}
		if node.Right != nil {
			rightIndex := addNode(node.Right)
			graph[index] = append(graph[index], rightIndex)
			graph[rightIndex] = append(graph[rightIndex], index)
			stack = append(stack, node.Right)
		}
	}

	answer := -1 << 60
	var dfs func(node, parent, currentSum int, used map[int]struct{})
	dfs = func(node, parent, currentSum int, used map[int]struct{}) {
		if currentSum > answer {
			answer = currentSum
		}
		for _, neighbor := range graph[node] {
			if neighbor == parent {
				continue
			}
			neighborValue := values[neighbor]
			if _, ok := used[neighborValue]; ok {
				continue
			}
			used[neighborValue] = struct{}{}
			dfs(neighbor, node, currentSum+neighborValue, used)
			delete(used, neighborValue)
		}
	}

	for start := range values {
		used := map[int]struct{}{values[start]: {}}
		dfs(start, -1, values[start], used)
	}

	return answer
}

// @lc code=end
