package leetcode

//
// @lc app=leetcode id=3893 lang=golang
//
// [3893] Maximum Team Size With Overlapping Intervals
//
// Notes
// For each interval [start,end], all intervals overlapping it are those that
// started by end minus those that ended before start. Sorting starts and ends
// lets us compute both counts with binary search. Time: O(n log n). Space:
// O(n).
//
// @lc code=start

import "sort"

func MaximumTeamSize3893(startTime []int, endTime []int) int {
	starts := append([]int(nil), startTime...)
	ends := append([]int(nil), endTime...)
	sort.Ints(starts)
	sort.Ints(ends)

	best := 1
	for i, start := range startTime {
		end := endTime[i]
		startedByEnd := sort.Search(len(starts), func(idx int) bool {
			return starts[idx] > end
		})
		endedBeforeStart := sort.SearchInts(ends, start)
		if current := startedByEnd - endedBeforeStart; current > best {
			best = current
		}
	}
	return best
}

// @lc code=end
