package main

func removeInterval(intervals [][]int, toBeRemoved []int) [][]int {
	removeStart, removeEnd := toBeRemoved[0], toBeRemoved[1]
	ans := [][]int{}

	for _, interval := range intervals {
		start, end := interval[0], interval[1]
		if end <= removeStart || start >= removeEnd {
			ans = append(ans, []int{start, end})
			continue
		}
		if start < removeStart {
			ans = append(ans, []int{start, removeStart})
		}
		if removeEnd < end {
			ans = append(ans, []int{removeEnd, end})
		}
	}

	return ans
}

/*
Explanation

For each interval, compare it with the interval to remove. If there is no
overlap, keep it unchanged. If there is overlap, at most two pieces survive:
the left part before removeStart and the right part after removeEnd.

No heap, tree, or merging structure is needed because the intervals are already
disjoint and sorted.

Edge cases: the removed interval covers a whole interval; it cuts an interval
in the middle; it only touches an endpoint, where no zero-length interval
should be emitted.

Time complexity: O(n).
Space complexity: O(n) for the answer.
*/
