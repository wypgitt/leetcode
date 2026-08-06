package leetcode

import "sort"

// CombinationSum39 backtracks over sorted candidates with reuse allowed. Passing
// the same start index permits reuse; sorting lets the loop stop once val exceeds
// the remaining target.
//
// Time: exponential in output size. Space: O(target/min(candidate)) recursion.
func CombinationSum39(candidates []int, target int) [][]int {
	sort.Ints(candidates)
	ans := [][]int{}
	path := []int{}
	var dfs func(int, int)
	dfs = func(start, remain int) {
		if remain == 0 {
			ans = append(ans, append([]int(nil), path...))
			return
		}
		for i := start; i < len(candidates); i++ {
			v := candidates[i]
			if v > remain {
				break
			}
			path = append(path, v)
			dfs(i, remain-v)
			path = path[:len(path)-1]
		}
	}
	dfs(0, target)
	return ans
}
