package leetcode

// KillProcess582 builds parent -> children adjacency, then BFSes from the killed
// process to collect the entire subtree that must terminate.
//
// Go data structure note: map[int][]int is the adjacency list; []int with a head
// index is the queue.
//
// Time: O(n+k), where k killed descendants are traversed. Space: O(n).
func KillProcess582(pid []int, ppid []int, kill int) []int {
	children := map[int][]int{}
	for i, child := range pid {
		parent := ppid[i]
		children[parent] = append(children[parent], child)
	}
	ans := []int{}
	queue := []int{kill}
	for head := 0; head < len(queue); head++ {
		cur := queue[head]
		ans = append(ans, cur)
		queue = append(queue, children[cur]...)
	}
	return ans
}
