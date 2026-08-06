package leetcode

//
// @lc app=leetcode id=3882 lang=golang
//
// [3882] Minimum XOR Path in a Grid
//
// Notes
// For each cell, keep the set of all XOR values reachable at that cell from the
// top or left. The DP array is one row wide: dp[col] is the previous-row set
// before update and the current-row set after update. Go map[int]struct{} is
// the set representation. Time: O(R*C*S), where S is reachable XOR count. Space:
// O(C*S).
//
// @lc code=start

func MinCost3882(grid [][]int) int {
	rows, cols := len(grid), len(grid[0])
	dp := make([]map[int]struct{}, cols)

	for row := 0; row < rows; row++ {
		for col := 0; col < cols; col++ {
			value := grid[row][col]
			if row == 0 && col == 0 {
				dp[col] = map[int]struct{}{value: {}}
				continue
			}

			reachable := map[int]struct{}{}
			if row > 0 {
				for previousXor := range dp[col] {
					reachable[previousXor^value] = struct{}{}
				}
			}
			if col > 0 {
				for previousXor := range dp[col-1] {
					reachable[previousXor^value] = struct{}{}
				}
			}
			dp[col] = reachable
		}
	}

	answer := 1 << 60
	for value := range dp[cols-1] {
		if value < answer {
			answer = value
		}
	}
	return answer
}

// @lc code=end
