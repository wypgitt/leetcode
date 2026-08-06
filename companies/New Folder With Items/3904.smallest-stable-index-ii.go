package leetcode

//
// @lc app=leetcode id=3904 lang=golang
//
// [3904] Smallest Stable Index II
//
// Notes
// suffixMin[i] stores the minimum value from i to the end, while prefixMax is
// updated left to right. The first index where prefixMax - suffixMin[i] <= k is
// the stable index requested by the Python solution. Time: O(n). Space: O(n).
//
// @lc code=start

func FirstStableIndex3904(nums []int, k int) int {
	n := len(nums)
	suffixMin := make([]int, n)
	suffixMin[n-1] = nums[n-1]
	for i := n - 2; i >= 0; i-- {
		if nums[i] < suffixMin[i+1] {
			suffixMin[i] = nums[i]
		} else {
			suffixMin[i] = suffixMin[i+1]
		}
	}

	prefixMax := 0
	for i, value := range nums {
		if value > prefixMax {
			prefixMax = value
		}
		if prefixMax-suffixMin[i] <= k {
			return i
		}
	}
	return -1
}

// @lc code=end
