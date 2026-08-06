package leetcode

// Combine77 backtracks in increasing order. The start value prevents duplicate
// orders, and the loop upper bound prunes branches that cannot fill k slots.
//
// Time: O(C(n,k)*k). Space: O(k) excluding output.
func Combine77(n int, k int) [][]int {
	ans := [][]int{}
	path := []int{}
	var dfs func(int)
	dfs = func(start int) {
		if len(path) == k {
			ans = append(ans, append([]int(nil), path...))
			return
		}
		need := k - len(path)
		for v := start; v <= n-need+1; v++ {
			path = append(path, v)
			dfs(v + 1)
			path = path[:len(path)-1]
		}
	}
	dfs(1)
	return ans
}
