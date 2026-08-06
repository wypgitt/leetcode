package leetcode

// UniquePaths62 uses one-row DP where dp[c] is ways to reach column c in the
// current row. Each cell adds ways from the left to ways from above.
//
// Time: O(m*n). Space: O(n).
func UniquePaths62(m int, n int) int {
	dp := make([]int, n)
	for i := range dp {
		dp[i] = 1
	}
	for r := 1; r < m; r++ {
		for c := 1; c < n; c++ {
			dp[c] += dp[c-1]
		}
	}
	return dp[n-1]
}
