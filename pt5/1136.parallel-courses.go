package main

func minimumSemesters(n int, relations [][]int) int {
	graph := make([][]int, n+1)
	indegree := make([]int, n+1)
	for _, relation := range relations {
		before, after := relation[0], relation[1]
		graph[before] = append(graph[before], after)
		indegree[after]++
	}

	queue := []int{}
	for course := 1; course <= n; course++ {
		if indegree[course] == 0 {
			queue = append(queue, course)
		}
	}

	taken, semesters := 0, 0
	for len(queue) > 0 {
		semesters++
		levelSize := len(queue)
		for i := 0; i < levelSize; i++ {
			course := queue[0]
			queue = queue[1:]
			taken++
			for _, nextCourse := range graph[course] {
				indegree[nextCourse]--
				if indegree[nextCourse] == 0 {
					queue = append(queue, nextCourse)
				}
			}
		}
	}

	if taken == n {
		return semesters
	}
	return -1
}

