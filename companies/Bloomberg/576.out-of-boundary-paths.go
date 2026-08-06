package leetcode

// FindPaths576 memoizes dp(r,c,moves), the number of paths that leave the grid
// from a cell with moves remaining. Moving outside contributes one successful
// path; staying inside with no moves contributes zero.
//
// Go data structure note: a small struct key in map[state]int replaces Python's
// lru_cache.
//
// Time: O(m*n*maxMove). Space: O(m*n*maxMove).
func FindPaths576(m int, n int, maxMove int, startRow int, startColumn int) int {
	const mod = 1000000007
	type state struct{ r, c, moves int }
	memo := map[state]int{}
	var dp func(int, int, int) int
	dp = func(r, c, moves int) int {
		if r < 0 || r >= m || c < 0 || c >= n {
			return 1
		}
		if moves == 0 {
			return 0
		}
		key := state{r, c, moves}
		if v, ok := memo[key]; ok {
			return v
		}
		ans := (((dp(r+1, c, moves-1)+dp(r-1, c, moves-1))%mod+dp(r, c+1, moves-1))%mod + dp(r, c-1, moves-1)) % mod
		memo[key] = ans
		return ans
	}
	return dp(startRow, startColumn, maxMove)
}
