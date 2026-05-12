package main

func numRollsToTarget(n int, k int, target int) int {
	const mod = 1_000_000_007
	dp := make([]int, target+1)
	dp[0] = 1

	for dice := 0; dice < n; dice++ {
		next := make([]int, target+1)
		for total := 1; total <= target; total++ {
			ways := 0
			limit := k
			if total < limit {
				limit = total
			}
			for face := 1; face <= limit; face++ {
				ways = (ways + dp[total-face]) % mod
			}
			next[total] = ways
		}
		dp = next
	}

	return dp[target]
}
