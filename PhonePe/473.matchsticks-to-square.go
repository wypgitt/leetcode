package leetcode

import "sort"

// Makesquare473 backtracks by assigning each stick to one of four side sums.
// Descending order fails large impossible sticks early; skipping equal current
// side sums removes symmetric duplicate states.
//
// Time: worst-case O(4^n), heavily pruned. Space: O(n) recursion depth.
func Makesquare473(matchsticks []int) bool {
	total := 0
	for _, x := range matchsticks {
		total += x
	}
	if len(matchsticks) < 4 || total%4 != 0 {
		return false
	}
	side := total / 4
	sort.Sort(sort.Reverse(sort.IntSlice(matchsticks)))
	if matchsticks[0] > side {
		return false
	}
	sides := [4]int{}
	var dfs func(int) bool
	dfs = func(i int) bool {
		if i == len(matchsticks) {
			return sides[0] == side && sides[1] == side && sides[2] == side && sides[3] == side
		}
		length := matchsticks[i]
		seen := map[int]bool{}
		for j := 0; j < 4; j++ {
			if seen[sides[j]] || sides[j]+length > side {
				continue
			}
			seen[sides[j]] = true
			sides[j] += length
			if dfs(i + 1) {
				return true
			}
			sides[j] -= length
		}
		return false
	}
	return dfs(0)
}
