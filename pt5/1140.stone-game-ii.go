package main

func stoneGameII(piles []int) int {
	n := len(piles)
	suffix := make([]int, n+1)
	for i := n - 1; i >= 0; i-- {
		suffix[i] = suffix[i+1] + piles[i]
	}

	memo := make([][]int, n)
	for i := range memo {
		memo[i] = make([]int, n+1)
		for j := range memo[i] {
			memo[i][j] = -1
		}
	}

	var dfs func(int, int) int
	dfs = func(i, m int) int {
		if i >= n {
			return 0
		}
		if 2*m >= n-i {
			return suffix[i]
		}
		if memo[i][m] != -1 {
			return memo[i][m]
		}

		best := 0
		for x := 1; x <= 2*m; x++ {
			nextM := m
			if x > nextM {
				nextM = x
			}
			opponent := dfs(i+x, nextM)
			if suffix[i]-opponent > best {
				best = suffix[i] - opponent
			}
		}
		memo[i][m] = best
		return best
	}

	return dfs(0, 1)
}

