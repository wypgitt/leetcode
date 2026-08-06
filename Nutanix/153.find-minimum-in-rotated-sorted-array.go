package leetcode

// FindMin153 binary-searches the rotation pivot. If nums[mid] > nums[right], the
// minimum is to the right; otherwise it is at mid or to the left.
//
// Time: O(log n). Space: O(1).
func FindMin153(nums []int) int {
	l, r := 0, len(nums)-1
	for l < r {
		m := (l + r) / 2
		if nums[m] > nums[r] {
			l = m + 1
		} else {
			r = m
		}
	}
	return nums[l]
}
