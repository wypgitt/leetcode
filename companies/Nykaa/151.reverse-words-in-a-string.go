package leetcode

import "strings"

// ReverseWords151 splits on whitespace, reverses the resulting word list, and
// joins with single spaces. strings.Fields handles repeated and leading/trailing
// spaces.
//
// Time: O(n). Space: O(n).
func ReverseWords151(s string) string {
	parts := strings.Fields(s)
	for l, r := 0, len(parts)-1; l < r; l, r = l+1, r-1 {
		parts[l], parts[r] = parts[r], parts[l]
	}
	return strings.Join(parts, " ")
}
