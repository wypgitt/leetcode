package leetcode

//
// @lc app=leetcode id=3874 lang=golang
//
// [3874] Valid Subarrays With Exactly One Peak
//
// Notes
// Enumerate all strict local peaks. For each peak, choose a left boundary after
// the previous peak and within distance k, and a right boundary before the next
// peak and within distance k. Multiplying those independent choices counts every
// subarray with exactly that one peak. Time: O(n). Space: O(number of peaks).
//
// @lc code=start

func ValidSubarrays3874(nums []int, k int) int {
	n := len(nums)
	peaks := []int{}
	for index := 1; index < n-1; index++ {
		if nums[index] > nums[index-1] && nums[index] > nums[index+1] {
			peaks = append(peaks, index)
		}
	}

	answer := 0
	for peakIndex, peak := range peaks {
		previousPeak := -1
		if peakIndex > 0 {
			previousPeak = peaks[peakIndex-1]
		}
		nextPeak := n
		if peakIndex+1 < len(peaks) {
			nextPeak = peaks[peakIndex+1]
		}

		leftMin := max3874(0, max3874(peak-k, previousPeak+1))
		rightMax := min3874(n-1, min3874(peak+k, nextPeak-1))
		answer += (peak - leftMin + 1) * (rightMax - peak + 1)
	}

	return answer
}

func min3874(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func max3874(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// @lc code=end
