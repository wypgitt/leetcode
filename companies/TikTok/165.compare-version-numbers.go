package leetcode

import (
	"strconv"
	"strings"
)

// CompareVersion165 compares dot-separated integer revisions, treating missing
// trailing revisions as zero. strconv.Atoi naturally ignores leading zeros.
//
// Time: O(m+n). Space: O(m+n) for split parts.
func CompareVersion165(version1 string, version2 string) int {
	a, b := strings.Split(version1, "."), strings.Split(version2, ".")
	max := len(a)
	if len(b) > max {
		max = len(b)
	}
	for i := 0; i < max; i++ {
		x, y := 0, 0
		if i < len(a) {
			x, _ = strconv.Atoi(a[i])
		}
		if i < len(b) {
			y, _ = strconv.Atoi(b[i])
		}
		if x < y {
			return -1
		}
		if x > y {
			return 1
		}
	}
	return 0
}
