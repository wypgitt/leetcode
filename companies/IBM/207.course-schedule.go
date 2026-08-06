package leetcode

// CanFinish207 uses Kahn's topological sort. Courses with indegree zero enter a
// queue; removing them reduces dependent indegrees. All courses are finishable
// exactly when every node is processed.
//
// Time: O(V+E). Space: O(V+E).
func CanFinish207(numCourses int, prerequisites [][]int) bool {
	graph := make([][]int, numCourses)
	indeg := make([]int, numCourses)
	for _, p := range prerequisites {
		course, pre := p[0], p[1]
		graph[pre] = append(graph[pre], course)
		indeg[course]++
	}
	q := []int{}
	for i, d := range indeg {
		if d == 0 {
			q = append(q, i)
		}
	}
	taken := 0
	for head := 0; head < len(q); head++ {
		node := q[head]
		taken++
		for _, nxt := range graph[node] {
			indeg[nxt]--
			if indeg[nxt] == 0 {
				q = append(q, nxt)
			}
		}
	}
	return taken == numCourses
}
