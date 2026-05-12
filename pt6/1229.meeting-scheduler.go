package main

import "sort"

func minAvailableDuration(slots1 [][]int, slots2 [][]int, duration int) []int {
	sort.Slice(slots1, func(i, j int) bool { return slots1[i][0] < slots1[j][0] })
	sort.Slice(slots2, func(i, j int) bool { return slots2[i][0] < slots2[j][0] })

	i, j := 0, 0
	for i < len(slots1) && j < len(slots2) {
		start := maxInt(slots1[i][0], slots2[j][0])
		end := minInt(slots1[i][1], slots2[j][1])
		if end-start >= duration {
			return []int{start, start + duration}
		}
		if slots1[i][1] < slots2[j][1] {
			i++
		} else {
			j++
		}
	}

	return []int{}
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func maxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}

/*
Explanation

Sort both people's available slots by start time. Use two pointers to compare
one slot from each list. Their overlap is [max(starts), min(ends)]. If that
overlap is at least duration, it is the earliest valid meeting because both
lists are scanned in chronological order.

If the overlap is too short, advance the slot that ends earlier. That slot
cannot produce a later valid overlap with the current other slot, and future
slots start no earlier.

Edge cases: exact duration overlap is valid; no overlap returns an empty slice;
input can be unsorted.

Time complexity: O(n log n + m log m) for sorting, then O(n + m).
Space complexity: O(1) besides sort stack.
*/
