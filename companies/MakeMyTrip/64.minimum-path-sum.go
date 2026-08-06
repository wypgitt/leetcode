package leetcode

// MinPathSum64 stores the best cost to each column in a one-dimensional DP row.
// Each cell takes its value plus the cheaper of top (old dp[c]) and left
// (dp[c-1]), with first row/column handled by their single possible direction.
//
// Time: O(m*n). Space: O(n).
func MinPathSum64(grid [][]int) int {
	n := len(grid[0])
	dp := make([]int, n)
	for r := 0; r < len(grid); r++ {
		for c := 0; c < n; c++ {
			if r == 0 && c == 0 {
				dp[c] = grid[r][c]
			} else if r == 0 {
				dp[c] = dp[c-1] + grid[r][c]
			} else if c == 0 {
				dp[c] += grid[r][c]
			} else {
				dp[c] = minInt(dp[c], dp[c-1]) + grid[r][c]
			}
		}
	}
	return dp[n-1]
}
