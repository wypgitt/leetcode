package leetcode

// FindOrder210 is Kahn's topological sort and returns the processed order. If a
// cycle prevents processing all courses, the valid order does not exist.
//
// Time: O(V+E). Space: O(V+E).
func FindOrder210(numCourses int, prerequisites [][]int) []int {
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
	order := []int{}
	for head := 0; head < len(q); head++ {
		node := q[head]
		order = append(order, node)
		for _, nxt := range graph[node] {
			indeg[nxt]--
			if indeg[nxt] == 0 {
				q = append(q, nxt)
			}
		}
	}
	if len(order) != numCourses {
		return []int{}
	}
	return order
}
