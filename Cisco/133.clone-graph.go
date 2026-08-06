package leetcode

// GraphNode133 is the graph node used by CloneGraph133.
type GraphNode133 struct {
	Val       int
	Neighbors []*GraphNode133
}

// CloneGraph133 performs DFS with a map from original node pointers to clone
// pointers. The map both preserves shared/cyclic structure and prevents infinite
// recursion on cycles.
//
// Time: O(V+E). Space: O(V).
func CloneGraph133(node *GraphNode133) *GraphNode133 {
	clones := map[*GraphNode133]*GraphNode133{}
	var clone func(*GraphNode133) *GraphNode133
	clone = func(cur *GraphNode133) *GraphNode133 {
		if cur == nil {
			return nil
		}
		if c := clones[cur]; c != nil {
			return c
		}
		copied := &GraphNode133{Val: cur.Val}
		clones[cur] = copied
		for _, nei := range cur.Neighbors {
			copied.Neighbors = append(copied.Neighbors, clone(nei))
		}
		return copied
	}
	return clone(node)
}
