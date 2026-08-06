package leetcode

// LoudAndRich851 builds edges from each poorer person to richer people, then
// memoized DFS returns the quietest reachable richer-or-self person. The answer
// slice doubles as memoization.
//
// Go data structure note: map[int][]int is a compact adjacency list for the DAG;
// ans initialized to -1 marks unresolved nodes.
//
// Time: O(n+e). Space: O(n+e).
func LoudAndRich851(richer [][]int, quiet []int) []int {
	richerThan := map[int][]int{}
	for _, edge := range richer {
		rich, poor := edge[0], edge[1]
		richerThan[poor] = append(richerThan[poor], rich)
	}
	ans := make([]int, len(quiet))
	for i := range ans {
		ans[i] = -1
	}
	var dfs func(int) int
	dfs = func(person int) int {
		if ans[person] != -1 {
			return ans[person]
		}
		best := person
		for _, rich := range richerThan[person] {
			candidate := dfs(rich)
			if quiet[candidate] < quiet[best] {
				best = candidate
			}
		}
		ans[person] = best
		return best
	}
	for person := range quiet {
		dfs(person)
	}
	return ans
}
