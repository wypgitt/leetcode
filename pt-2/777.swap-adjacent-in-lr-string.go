package leetcode

import "strings"

// CanTransform777 first verifies the non-X piece order is unchanged. Then two
// pointers compare positions: L may only move left, so its final index cannot be
// greater; R may only move right, so its final index cannot be smaller.
//
// Time: O(n). Space: O(n) due to ReplaceAll; this can be folded into the scan
// for O(1) extra space.
func CanTransform777(start string, result string) bool {
	if strings.ReplaceAll(start, "X", "") != strings.ReplaceAll(result, "X", "") {
		return false
	}
	i, j, n := 0, 0, len(start)
	for i < n && j < n {
		for i < n && start[i] == 'X' {
			i++
		}
		for j < n && result[j] == 'X' {
			j++
		}
		if i == n || j == n {
			break
		}
		if start[i] == 'L' && i < j {
			return false
		}
		if start[i] == 'R' && i > j {
			return false
		}
		i++
		j++
	}
	return true
}
