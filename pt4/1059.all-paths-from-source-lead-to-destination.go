package main

/*
1059. All Paths from Source Lead to Destination
*/
func leadsToDestination(n int, edges [][]int, source int, destination int) bool {
	graph := make([][]int, n)
	for _, edge := range edges {
		graph[edge[0]] = append(graph[edge[0]], edge[1])
	}

	state := make([]int, n)
	type frame struct {
		node      int
		nextEdge  int
		activated bool
	}

	stack := []frame{{node: source}}
	for len(stack) > 0 {
		topIndex := len(stack) - 1
		top := &stack[topIndex]
		node := top.node

		if !top.activated {
			if len(graph[node]) == 0 {
				if node != destination {
					return false
				}
				state[node] = 2
				stack = stack[:topIndex]
				continue
			}
			state[node] = 1
			top.activated = true
		}

		if top.nextEdge == len(graph[node]) {
			state[node] = 2
			stack = stack[:topIndex]
			continue
		}

		neighbor := graph[node][top.nextEdge]
		top.nextEdge++

		if state[neighbor] == 1 {
			return false
		}
		if state[neighbor] == 0 {
			stack = append(stack, frame{node: neighbor})
		}
	}

	return true
}

/*
Interview Explanation

Core idea:
All paths from source must terminate at destination, and there can be no
reachable cycle. A reachable dead end that is not destination fails. A
reachable cycle fails because it creates an infinite path or infinitely many
paths.

Go data structures:
- [][]int adjacency list stores the directed graph.
- []int state is DFS coloring: 0 = unvisited, 1 = currently visiting,
  2 = proven safe.
- []frame is an explicit DFS stack. Each frame stores the node and the next
  outgoing edge to process, avoiding recursion depth concerns for 10,000 nodes.

Algorithm:
1. Build the graph.
2. DFS from source using color states.
3. If a node has no outgoing edges, it is valid only if it is destination.
4. Seeing a state-1 neighbor means a reachable cycle, so return false.
5. A node is marked safe only after all outgoing neighbors are safe.

Correctness:
The terminal check ensures any path that stops must stop at destination. The
visiting color detects cycles reachable from source, violating the finite-path
requirement. If every outgoing neighbor of a node is safe, then every path from
that node also eventually ends at destination. Therefore the source is safe if
and only if all paths from source lead to destination.

Complexity:
Each reachable node and edge is processed once, so time is O(n+e). The graph,
state array, and stack use O(n+e) space.

Edge cases:
- source == destination with no outgoing edges returns true.
- A path to a non-destination terminal node returns false.
- Reachable self-loop or cycle returns false.
- Unreachable bad components do not matter.
*/
