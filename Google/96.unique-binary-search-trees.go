package leetcode

// NumTrees96 is the Catalan DP: choosing a root leaves independent left and
// right subtree sizes, so dp[nodes] sums dp[left]*dp[right] over all splits.
//
// Time: O(n^2). Space: O(n).
func NumTrees96(n int) int {
	dp := make([]int, n+1)
	dp[0] = 1
	if n >= 1 {
		dp[1] = 1
	}
	for nodes := 2; nodes <= n; nodes++ {
		for left := 0; left < nodes; left++ {
			dp[nodes] += dp[left] * dp[nodes-1-left]
		}
	}
	return dp[n]
}
