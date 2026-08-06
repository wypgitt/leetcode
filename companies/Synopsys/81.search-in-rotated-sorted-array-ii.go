package leetcode

// Search81 is rotated binary search with duplicates. When left, mid, and right
// are equal, the sorted half cannot be identified, so both ends shrink; otherwise
// the usual sorted-half logic applies.
//
// Average time: O(log n), worst-case O(n). Space: O(1).
func Search81(nums []int, target int) bool {
	l, r := 0, len(nums)-1
	for l <= r {
		m := (l + r) / 2
		if nums[m] == target {
			return true
		}
		if nums[l] == nums[m] && nums[m] == nums[r] {
			l++
			r--
		} else if nums[l] <= nums[m] {
			if nums[l] <= target && target < nums[m] {
				r = m - 1
			} else {
				l = m + 1
			}
		} else {
			if nums[m] < target && target <= nums[r] {
				l = m + 1
			} else {
				r = m - 1
			}
		}
	}
	return false
}
