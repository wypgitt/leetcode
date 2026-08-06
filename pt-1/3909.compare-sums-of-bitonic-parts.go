package leetcode

//
// @lc app=leetcode id=3909 lang=golang
//
// [3909] Compare Sums of Bitonic Parts
//
// Notes
// Find the first maximum element as the peak. Sum the ascending part through
// the peak and the descending part from the peak, then compare the totals:
// return 0 for ascending larger, 1 for descending larger, and -1 for equal.
// Time: O(n). Space: O(1).
//
// @lc code=start

func CompareBitonicSums3909(nums []int) int {
	peak := 0
	for i := 1; i < len(nums); i++ {
		if nums[i] > nums[peak] {
			peak = i
		}
	}

	ascendingSum := 0
	for i := 0; i <= peak; i++ {
		ascendingSum += nums[i]
	}

	descendingSum := 0
	for i := peak; i < len(nums); i++ {
		descendingSum += nums[i]
	}

	if ascendingSum > descendingSum {
		return 0
	}
	if descendingSum > ascendingSum {
		return 1
	}
	return -1
}

// @lc code=end
