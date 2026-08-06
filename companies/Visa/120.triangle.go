package leetcode

// MinimumTotal120 is bottom-up DP. The best path from a cell is its value plus
// the cheaper of the two adjacent cells below. A single dp slice initialized to
// the last row satisfies the O(rows) space follow-up.
//
// Time: O(total cells). Space: O(rows).
func MinimumTotal120(triangle [][]int) int {
	dp := append([]int(nil), triangle[len(triangle)-1]...)
	for r := len(triangle) - 2; r >= 0; r-- {
		for c := 0; c < len(triangle[r]); c++ {
			dp[c] = triangle[r][c] + minInt(dp[c], dp[c+1])
		}
	}
	return dp[0]
}
