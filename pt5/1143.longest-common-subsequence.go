package main

func longestCommonSubsequence(text1 string, text2 string) int {
	if len(text2) > len(text1) {
		text1, text2 = text2, text1
	}

	dp := make([]int, len(text2)+1)
	for i := 0; i < len(text1); i++ {
		previousDiagonal := 0
		for j := 1; j <= len(text2); j++ {
			saved := dp[j]
			if text1[i] == text2[j-1] {
				dp[j] = previousDiagonal + 1
			} else if dp[j-1] > dp[j] {
				dp[j] = dp[j-1]
			}
			previousDiagonal = saved
		}
	}

	return dp[len(text2)]
}

