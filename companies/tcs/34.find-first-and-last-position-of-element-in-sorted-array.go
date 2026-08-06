package leetcode

import "sort"

// SearchRange34 uses lower_bound twice: first target position and first value
// greater than target minus one. Validation handles absent targets.
//
// Time: O(log n). Space: O(1).
func SearchRange34(nums []int, target int) []int {
	first := sort.Search(len(nums), func(i int) bool { return nums[i] >= target })
	if first == len(nums) || nums[first] != target {
		return []int{-1, -1}
	}
	last := sort.Search(len(nums), func(i int) bool { return nums[i] >= target+1 }) - 1
	return []int{first, last}
}
