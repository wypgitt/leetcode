package leetcode

import "sort"

// FindRightInterval436 sorts interval starts with original indices, then uses
// binary search to find the first start >= each interval end.
//
// Time: O(n log n). Space: O(n).
func FindRightInterval436(intervals [][]int) []int {
	type pair struct{ start, idx int }
	starts := make([]pair, len(intervals))
	for i, in := range intervals {
		starts[i] = pair{in[0], i}
	}
	sort.Slice(starts, func(i, j int) bool {
		if starts[i].start == starts[j].start {
			return starts[i].idx < starts[j].idx
		}
		return starts[i].start < starts[j].start
	})
	ans := make([]int, len(intervals))
	for i, in := range intervals {
		end := in[1]
		pos := sort.Search(len(starts), func(j int) bool { return starts[j].start >= end })
		if pos == len(starts) {
			ans[i] = -1
		} else {
			ans[i] = starts[pos].idx
		}
	}
	return ans
}
