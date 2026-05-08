package leetcode

//
// @lc app=leetcode id=3802 lang=golang
//
// [3802] Number of Ways to Paint Sheets
//
// Notes
// The number of valid color choices for a split changes only when one of the
// threshold expressions crosses a limit value, so scan compressed boundary
// intervals instead of all split positions. For each interval, binary search the
// sorted limits to count colors that can cover each side and subtract same-color
// double counts. Time: O(m log m). Space: O(m).
//
// @lc code=start

import "sort"

const mod3802 = 1_000_000_007

func NumberOfWays3802(n int, limit []int) int {
	limits := append([]int(nil), limit...)
	sort.Ints(limits)
	m := len(limits)

	boundarySet := map[int]struct{}{1: {}, n: {}}
	for _, value := range limits {
		for _, point := range []int{value, value + 1, n - value, n - value + 1} {
			if 1 <= point && point <= n {
				boundarySet[point] = struct{}{}
			}
		}
	}

	points := make([]int, 0, len(boundarySet))
	for point := range boundarySet {
		points = append(points, point)
	}
	sort.Ints(points)

	answer := int64(0)
	for i := 0; i+1 < len(points); i++ {
		left, right := points[i], points[i+1]
		if left > n-1 {
			break
		}
		length := min3802(right, n) - left
		if length <= 0 {
			continue
		}

		firstChoices := countAtLeast3802(limits, left, m)
		secondChoices := countAtLeast3802(limits, n-left, m)
		sameColor := countAtLeast3802(limits, max3802(left, n-left), m)
		perSplit := int64(firstChoices*secondChoices - sameColor)
		answer = (answer + perSplit*int64(length)) % mod3802
	}

	return int(answer)
}

func countAtLeast3802(limits []int, need int, size int) int {
	return size - sort.SearchInts(limits, need)
}

func min3802(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func max3802(a, b int) int {
	if a > b {
		return a
	}
	return b
}

// @lc code=end
