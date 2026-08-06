package leetcode

import "sort"

// MinMoves2462 minimizes total absolute deviation by choosing a median target.
// Sorting exposes a median; either middle value is optimal for even lengths.
//
// Time: O(n log n). Space: O(1) extra besides the in-place sort.
func MinMoves2462(nums []int) int {
	sort.Ints(nums)
	median := nums[len(nums)/2]
	moves := 0
	for _, x := range nums {
		moves += absInt(x - median)
	}
	return moves
}
