package leetcode

import "strings"

// OptimalDivision553 maximizes nums[0]/nums[1]/... by minimizing the denominator:
// place every value after nums[0] inside one denominator expression. Values from
// nums[2:] effectively move to the numerator of the overall result.
//
// Time: O(n). Space: O(n) for the expression string.
func OptimalDivision553(nums []int) string {
	if len(nums) == 1 {
		return intToString(nums[0])
	}
	if len(nums) == 2 {
		return intToString(nums[0]) + "/" + intToString(nums[1])
	}
	parts := make([]string, len(nums)-1)
	for i := 1; i < len(nums); i++ {
		parts[i-1] = intToString(nums[i])
	}
	return intToString(nums[0]) + "/(" + strings.Join(parts, "/") + ")"
}
