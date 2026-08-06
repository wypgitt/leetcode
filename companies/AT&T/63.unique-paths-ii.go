package leetcode

// UniquePathsWithObstacles63 reuses one-row DP. An obstacle zeroes dp[c]
// because no path can stand there; otherwise dp[c] receives paths from left.
//
// Time: O(m*n). Space: O(n).
func UniquePathsWithObstacles63(obstacleGrid [][]int) int {
	n := len(obstacleGrid[0])
	dp := make([]int, n)
	if obstacleGrid[0][0] == 0 {
		dp[0] = 1
	}
	for r := 0; r < len(obstacleGrid); r++ {
		for c := 0; c < n; c++ {
			if obstacleGrid[r][c] == 1 {
				dp[c] = 0
			} else if c > 0 {
				dp[c] += dp[c-1]
			}
		}
	}
	return dp[n-1]
}
