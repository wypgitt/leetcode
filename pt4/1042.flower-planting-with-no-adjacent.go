package main

/*
1042. Flower Planting With No Adjacent
*/
func gardenNoAdj(n int, paths [][]int) []int {
	graph := make([][]int, n)
	for _, path := range paths {
		a, b := path[0]-1, path[1]-1
		graph[a] = append(graph[a], b)
		graph[b] = append(graph[b], a)
	}

	answer := make([]int, n)
	for garden := 0; garden < n; garden++ {
		used := [5]bool{}
		for _, neighbor := range graph[garden] {
			used[answer[neighbor]] = true
		}

		for flower := 1; flower <= 4; flower++ {
			if !used[flower] {
				answer[garden] = flower
				break
			}
		}
	}

	return answer
}

/*
Interview Explanation

Core idea:
Each garden has at most three neighbors, while four flower types are available.
When coloring any garden, at most three colors can be forbidden, so there is
always a valid color left.

Go data structures:
- [][]int adjacency list represents the sparse graph.
- []int answer stores the assigned flower for each garden.
- [5]bool marks used neighbor colors 1 through 4.

Algorithm:
1. Build the undirected graph using 0-indexed garden ids.
2. Visit gardens in order.
3. Mark colors already assigned to neighbors.
4. Choose the first unused color from 1..4.

Correctness:
When a garden is colored, it avoids every color already used by its neighbors.
Future neighbors will also see this garden's color and avoid it. Since degree
is at most 3 and there are 4 colors, the greedy step always succeeds, and every
edge ends with different colors on its endpoints.

Complexity:
Time is O(n+p), where p is len(paths). Space is O(n+p).

Edge cases:
- No paths: every garden can use color 1.
- Triangle uses three colors.
- Complete graph on four gardens uses all four colors.
*/
