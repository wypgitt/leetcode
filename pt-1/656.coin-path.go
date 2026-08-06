package leetcode

//
// @lc app=leetcode id=656 lang=golang
//
// [656] Coin Path
//
// Notes
// DP from right to left. dp[i] is the cheapest cost from i to the end; scanning
// next positions in increasing order preserves the lexicographically smallest
// path when costs tie because the first equal-cost candidate is kept. nextIndex
// reconstructs the 1-indexed path. Time: O(n*maxJump). Space: O(n).
//
// @lc code=start

func CheapestJump656(coins []int, maxJump int) []int {
	n := len(coins)
	const infinity = 1 << 60

	dp := make([]int, n)
	nextIndex := make([]int, n)
	for i := range dp {
		dp[i] = infinity
		nextIndex[i] = -1
	}
	if coins[n-1] != -1 {
		dp[n-1] = coins[n-1]
	}

	for index := n - 2; index >= 0; index-- {
		if coins[index] == -1 {
			continue
		}
		furthest := index + maxJump
		if furthest > n-1 {
			furthest = n - 1
		}
		for candidate := index + 1; candidate <= furthest; candidate++ {
			if dp[candidate] == infinity {
				continue
			}
			totalCost := coins[index] + dp[candidate]
			if totalCost < dp[index] {
				dp[index] = totalCost
				nextIndex[index] = candidate
			}
		}
	}

	if dp[0] == infinity {
		return []int{}
	}

	path := []int{}
	for index := 0; index != -1; index = nextIndex[index] {
		path = append(path, index+1)
		if index == n-1 {
			break
		}
	}
	return path
}

// @lc code=end
