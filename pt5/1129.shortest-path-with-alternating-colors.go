package main

func shortestAlternatingPaths(n int, redEdges [][]int, blueEdges [][]int) []int {
	graph := make([][][]int, 2)
	graph[0] = make([][]int, n)
	graph[1] = make([][]int, n)

	for _, edge := range redEdges {
		graph[0][edge[0]] = append(graph[0][edge[0]], edge[1])
	}
	for _, edge := range blueEdges {
		graph[1][edge[0]] = append(graph[1][edge[0]], edge[1])
	}

	answer := make([]int, n)
	for i := range answer {
		answer[i] = -1
	}

	type state struct {
		node      int
		lastColor int
		distance  int
	}

	visited := make([][2]bool, n)
	queue := []state{{node: 0, lastColor: 0}, {node: 0, lastColor: 1}}
	visited[0][0], visited[0][1] = true, true

	for head := 0; head < len(queue); head++ {
		current := queue[head]
		if answer[current.node] == -1 {
			answer[current.node] = current.distance
		}

		nextColor := 1 - current.lastColor
		for _, neighbor := range graph[nextColor][current.node] {
			if !visited[neighbor][nextColor] {
				visited[neighbor][nextColor] = true
				queue = append(queue, state{node: neighbor, lastColor: nextColor, distance: current.distance + 1})
			}
		}
	}

	return answer
}

