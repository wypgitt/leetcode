package leetcode

//
// @lc app=leetcode id=474 lang=golang
//
// [474] Ones and Zeroes
//
// Notes
// This is 0/1 knapsack with two capacities: available zeroes and ones. Iterate
// capacities backward for each string so every string is used at most once.
// dp[z][o] is the best subset size within those capacities. Time: O(len(strs) *
// m * n). Space: O(m*n).
//
// @lc code=start

func FindMaxForm474(strs []string, m int, n int) int {
	dp := make([][]int, m+1)
	for i := range dp {
		dp[i] = make([]int, n+1)
	}

	for _, text := range strs {
		zeroes := 0
		for i := range text {
			if text[i] == '0' {
				zeroes++
			}
		}
		ones := len(text) - zeroes

		for zeroCapacity := m; zeroCapacity >= zeroes; zeroCapacity-- {
			for oneCapacity := n; oneCapacity >= ones; oneCapacity-- {
				candidate := dp[zeroCapacity-zeroes][oneCapacity-ones] + 1
				if candidate > dp[zeroCapacity][oneCapacity] {
					dp[zeroCapacity][oneCapacity] = candidate
				}
			}
		}
	}

	return dp[m][n]
}

// @lc code=end
