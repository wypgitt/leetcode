package leetcode

// MaximalSquare221 uses one-row DP. For a '1' cell, the square side ending there
// is 1 + min(top, left, top-left). prevDiag stores the top-left value from the
// previous row.
//
// Time: O(m*n). Space: O(n).
func MaximalSquare221(matrix [][]byte) int {
	if len(matrix) == 0 || len(matrix[0]) == 0 {
		return 0
	}
	cols := len(matrix[0])
	dp := make([]int, cols+1)
	best := 0
	for _, row := range matrix {
		prevDiag := 0
		for j := 1; j <= cols; j++ {
			top := dp[j]
			if row[j-1] == '1' {
				dp[j] = 1 + minInt(minInt(dp[j], dp[j-1]), prevDiag)
				best = maxInt(best, dp[j])
			} else {
				dp[j] = 0
			}
			prevDiag = top
		}
	}
	return best * best
}
