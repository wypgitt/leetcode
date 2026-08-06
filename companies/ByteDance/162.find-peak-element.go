package leetcode

// FindPeakElement162 binary-searches by slope. If nums[mid] < nums[mid+1], a
// peak exists to the right; otherwise a peak exists at mid or to the left.
//
// Time: O(log n). Space: O(1).
func FindPeakElement162(nums []int) int {
	l, r := 0, len(nums)-1
	for l < r {
		m := (l + r) / 2
		if nums[m] < nums[m+1] {
			l = m + 1
		} else {
			r = m
		}
	}
	return l
}
