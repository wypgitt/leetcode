package leetcode

import (
	"sort"
	"strconv"
	"strings"
)

// LargestNumber179 sorts numbers as strings by comparing concatenations a+b and
// b+a. This comparator puts the order that produces the larger final number
// first; all-leading-zero output is normalized to "0".
//
// Time: O(n log n * k). Space: O(n*k).
func LargestNumber179(nums []int) string {
	parts := make([]string, len(nums))
	for i, x := range nums {
		parts[i] = strconv.Itoa(x)
	}
	sort.Slice(parts, func(i, j int) bool { return parts[i]+parts[j] > parts[j]+parts[i] })
	ans := strings.Join(parts, "")
	if ans[0] == '0' {
		return "0"
	}
	return ans
}
