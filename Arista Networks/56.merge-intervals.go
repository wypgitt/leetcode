package leetcode

import "sort"

// Merge56 sorts intervals by start. After sorting, overlapping intervals appear
// consecutively, so the current merged interval is extended or finalized in one
// left-to-right scan.
//
// Time: O(n log n). Space: O(n) output.
func Merge56(intervals [][]int) [][]int {
	sort.Slice(intervals, func(i, j int) bool { return intervals[i][0] < intervals[j][0] })
	merged := [][]int{}
	for _, in := range intervals {
		if len(merged) == 0 || in[0] > merged[len(merged)-1][1] {
			merged = append(merged, []int{in[0], in[1]})
		} else if in[1] > merged[len(merged)-1][1] {
			merged[len(merged)-1][1] = in[1]
		}
	}
	return merged
}
