package leetcode

// WordBreak139 uses dp[i] to mean s[:i] can be segmented. A word set gives O(1)
// dictionary lookup, and checking only word lengths avoids scanning impossible
// split sizes.
//
// Time: O(n * number_of_distinct_lengths * slice_cost). Space: O(n + dict).
func WordBreak139(s string, wordDict []string) bool {
	words := map[string]bool{}
	lengths := map[int]bool{}
	for _, w := range wordDict {
		words[w] = true
		lengths[len(w)] = true
	}
	dp := make([]bool, len(s)+1)
	dp[0] = true
	for i := 1; i <= len(s); i++ {
		for l := range lengths {
			if i >= l && dp[i-l] && words[s[i-l:i]] {
				dp[i] = true
				break
			}
		}
	}
	return dp[len(s)]
}
