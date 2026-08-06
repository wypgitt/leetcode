package leetcode

//
// @lc app=leetcode id=3877 lang=golang
//
// [3877] Minimum Removals to Achieve Target XOR
//
// Notes
// Keep as many elements as possible while obtaining each XOR value. dp[x] is the
// maximum kept count with XOR x after scanning a prefix; for every value we may
// skip it or keep it and move to x^value. The answer is n minus the best kept
// count for target. Time: O(n * 2^14). Space: O(2^14).
//
// @lc code=start

func MinRemovals3877(nums []int, target int) int {
	const maxXor = 1 << 14
	const unreachable = -1 << 30

	dp := make([]int, maxXor)
	for i := range dp {
		dp[i] = unreachable
	}
	dp[0] = 0

	for _, value := range nums {
		next := append([]int(nil), dp...)
		for xorValue, keptCount := range dp {
			if keptCount == unreachable {
				continue
			}
			newXor := xorValue ^ value
			if keptCount+1 > next[newXor] {
				next[newXor] = keptCount + 1
			}
		}
		dp = next
	}

	if dp[target] == unreachable {
		return -1
	}
	return len(nums) - dp[target]
}

// @lc code=end
