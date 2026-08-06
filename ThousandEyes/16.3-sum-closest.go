package leetcode

import "sort"

// ThreeSumClosest16 sorts and then fixes one value while two pointers search the
// best remaining pair. Pointer movement follows sorted order: raise a low sum by
// moving left, lower a high sum by moving right.
//
// Time: O(n^2). Space: O(1).
func ThreeSumClosest16(nums []int, target int) int {
	sort.Ints(nums)
	closest := nums[0] + nums[1] + nums[2]
	for i := 0; i < len(nums)-2; i++ {
		l, r := i+1, len(nums)-1
		for l < r {
			sum := nums[i] + nums[l] + nums[r]
			if absInt(sum-target) < absInt(closest-target) {
				closest = sum
			}
			if sum == target {
				return target
			}
			if sum < target {
				l++
			} else {
				r--
			}
		}
	}
	return closest
}
