package leetcode

import "sort"

// TriangleNumber611 sorts sides and fixes nums[k] as the largest side. If
// nums[i]+nums[j] > nums[k], every index from i through j-1 also works with j.
//
// Time: O(n^2) after sorting. Space: O(1) extra.
func TriangleNumber611(nums []int) int {
	sort.Ints(nums)
	ans := 0
	for k := len(nums) - 1; k >= 2; k-- {
		i, j := 0, k-1
		for i < j {
			if nums[i]+nums[j] > nums[k] {
				ans += j - i
				j--
			} else {
				i++
			}
		}
	}
	return ans
}
