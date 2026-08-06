package leetcode

import "sort"

// ThreeSumSmaller259 sorts nums and fixes one index. If nums[i]+nums[left]+
// nums[right] < target, then every index between left and right works with left,
// contributing right-left triplets at once.
//
// Time: O(n^2). Space: O(1).
func ThreeSumSmaller259(nums []int, target int) int {
	sort.Ints(nums)
	count := 0
	for i := 0; i < len(nums)-2; i++ {
		l, r := i+1, len(nums)-1
		for l < r {
			if nums[i]+nums[l]+nums[r] < target {
				count += r - l
				l++
			} else {
				r--
			}
		}
	}
	return count
}
