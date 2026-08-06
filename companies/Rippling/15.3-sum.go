package leetcode

import "sort"

// ThreeSum15 sorts nums, fixes a unique anchor, and uses two pointers for the
// remaining pair. Duplicate anchors and duplicate pair values are skipped after
// emitting a triplet.
//
// Time: O(n^2). Space: O(1) excluding output.
func ThreeSum15(nums []int) [][]int {
	sort.Ints(nums)
	ans := [][]int{}
	n := len(nums)
	for i := 0; i < n-2; i++ {
		if i > 0 && nums[i] == nums[i-1] {
			continue
		}
		if nums[i] > 0 {
			break
		}
		l, r := i+1, n-1
		for l < r {
			sum := nums[i] + nums[l] + nums[r]
			if sum == 0 {
				ans = append(ans, []int{nums[i], nums[l], nums[r]})
				l++
				r--
				for l < r && nums[l] == nums[l-1] {
					l++
				}
				for l < r && nums[r] == nums[r+1] {
					r--
				}
			} else if sum < 0 {
				l++
			} else {
				r--
			}
		}
	}
	return ans
}
