package leetcode

import "sort"

// FourSum18 sorts nums, fixes two unique indices, and solves the remaining 2Sum
// with two pointers. Sorting makes duplicate suppression deterministic.
//
// Time: O(n^3). Space: O(1) excluding output.
func FourSum18(nums []int, target int) [][]int {
	sort.Ints(nums)
	ans := [][]int{}
	n := len(nums)
	for i := 0; i < n-3; i++ {
		if i > 0 && nums[i] == nums[i-1] {
			continue
		}
		for j := i + 1; j < n-2; j++ {
			if j > i+1 && nums[j] == nums[j-1] {
				continue
			}
			l, r := j+1, n-1
			for l < r {
				sum := nums[i] + nums[j] + nums[l] + nums[r]
				if sum == target {
					ans = append(ans, []int{nums[i], nums[j], nums[l], nums[r]})
					l++
					r--
					for l < r && nums[l] == nums[l-1] {
						l++
					}
					for l < r && nums[r] == nums[r+1] {
						r--
					}
				} else if sum < target {
					l++
				} else {
					r--
				}
			}
		}
	}
	return ans
}
