package main

import "sort"

func removeCoveredIntervals(intervals [][]int) int {
	sort.Slice(intervals, func(i, j int) bool {
		if intervals[i][0] == intervals[j][0] {
			return intervals[i][1] > intervals[j][1]
		}
		return intervals[i][0] < intervals[j][0]
	})

	remaining, farthestEnd := 0, 0
	for _, interval := range intervals {
		if interval[1] > farthestEnd {
			remaining++
			farthestEnd = interval[1]
		}
	}
	return remaining
}

/*
Explanation

Sort intervals by start ascending and end descending. After this ordering, an
interval is covered if its end is not greater than the farthest end seen so
far. Otherwise it survives and extends farthestEnd.

Sorting end descending for equal starts is critical: [1,4] must come before
[1,3] so the shorter interval is detected as covered.

Edge cases: same start; disjoint intervals; overlapping but not covered
intervals.

Time complexity: O(n log n).
Space complexity: O(1) besides sorting.
*/
