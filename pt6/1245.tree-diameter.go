package main

func treeDiameter(edges [][]int) int {
	if len(edges) == 0 {
		return 0
	}

	n := len(edges) + 1
	graph := make([][]int, n)
	for _, edge := range edges {
		a, b := edge[0], edge[1]
		graph[a] = append(graph[a], b)
		graph[b] = append(graph[b], a)
	}

	start, _ := farthestNode(graph, 0)
	_, diameter := farthestNode(graph, start)
	return diameter
}

func farthestNode(graph [][]int, start int) (int, int) {
	type item struct {
		node int
		dist int
	}

	queue := []item{{node: start, dist: 0}}
	seen := make([]bool, len(graph))
	seen[start] = true
	farNode, farDist := start, 0

	for head := 0; head < len(queue); head++ {
		cur := queue[head]
		if cur.dist > farDist {
			farNode, farDist = cur.node, cur.dist
		}
		for _, next := range graph[cur.node] {
			if !seen[next] {
				seen[next] = true
				queue = append(queue, item{node: next, dist: cur.dist + 1})
			}
		}
	}

	return farNode, farDist
}

/*
Explanation

In a tree, start from any node and find the farthest node A. A is an endpoint
of a diameter. Start from A and find the farthest node again; that distance is
the tree diameter.

The adjacency list is the natural Go representation for an undirected tree.
BFS uses a slice queue with a head index and a seen slice.

Edge cases: a single-node tree has no edges and diameter 0; a chain returns
n-1; a star returns 2.

Time complexity: O(n), two BFS traversals.
Space complexity: O(n).
*/
