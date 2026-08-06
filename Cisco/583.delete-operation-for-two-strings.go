package leetcode

//
// @lc app=leetcode id=583 lang=golang
//
// [583] Delete Operation for Two Strings
//
// Notes
// Minimum deletions equals len(word1)+len(word2)-2*LCS(word1,word2). Compute the
// LCS length with one rolling DP row over the shorter word. previousDiagonal
// stores dp[i-1][j-1] while dp[j] still holds the previous row's same-column
// value. Time: O(mn). Space: O(min(m,n)).
//
// @lc code=start

func MinDistance583(word1 string, word2 string) int {
	if len(word2) > len(word1) {
		word1, word2 = word2, word1
	}

	dp := make([]int, len(word2)+1)
	for i := range word1 {
		previousDiagonal := 0
		for index := 1; index <= len(word2); index++ {
			previousRowSameColumn := dp[index]
			if word1[i] == word2[index-1] {
				dp[index] = previousDiagonal + 1
			} else if dp[index-1] > dp[index] {
				dp[index] = dp[index-1]
			}
			previousDiagonal = previousRowSameColumn
		}
	}

	lcsLength := dp[len(word2)]
	return len(word1) + len(word2) - 2*lcsLength
}

// @lc code=end
