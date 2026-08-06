package leetcode

import "sort"

// CombinationSum2_40 backtracks over sorted candidates, using each index once.
// At each recursion depth, equal values after the first are skipped to prevent
// duplicate combinations.
//
// Time: O(2^n*n) including output copies. Space: O(n).
func CombinationSum2_40(candidates []int, target int) [][]int {
	sort.Ints(candidates)
	ans := [][]int{}
	path := []int{}
	var dfs func(int, int)
	dfs = func(start, remain int) {
		if remain == 0 {
			ans = append(ans, append([]int(nil), path...))
			return
		}
		prevSet := false
		prev := 0
		for i := start; i < len(candidates); i++ {
			v := candidates[i]
			if prevSet && v == prev {
				continue
			}
			if v > remain {
				break
			}
			path = append(path, v)
			dfs(i+1, remain-v)
			path = path[:len(path)-1]
			prev, prevSet = v, true
		}
	}
	dfs(0, target)
	return ans
}
