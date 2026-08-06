package leetcode

// MinDistance72 computes edit distance over prefixes with one DP row. dp[j] is
// the cost to convert the processed prefix of word1 to word2[:j]. prevDiag keeps
// the replace/match dependency from the previous row and previous column.
//
// Time: O(m*n). Space: O(n).
func MinDistance72(word1 string, word2 string) int {
	n := len(word2)
	dp := make([]int, n+1)
	for j := 0; j <= n; j++ {
		dp[j] = j
	}
	for i := 1; i <= len(word1); i++ {
		prevDiag := dp[0]
		dp[0] = i
		for j := 1; j <= n; j++ {
			old := dp[j]
			if word1[i-1] == word2[j-1] {
				dp[j] = prevDiag
			} else {
				dp[j] = 1 + minInt(minInt(dp[j], dp[j-1]), prevDiag)
			}
			prevDiag = old
		}
	}
	return dp[n]
}
