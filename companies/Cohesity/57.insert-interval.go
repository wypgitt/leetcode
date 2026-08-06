package leetcode

// Insert57 scans the already sorted non-overlapping intervals in three phases:
// before the new interval, overlapping with it, and after it. Only the middle
// phase changes the new interval boundaries.
//
// Time: O(n). Space: O(n) output.
func Insert57(intervals [][]int, newInterval []int) [][]int {
	ans := [][]int{}
	i, n := 0, len(intervals)
	start, end := newInterval[0], newInterval[1]
	for i < n && intervals[i][1] < start {
		ans = append(ans, intervals[i])
		i++
	}
	for i < n && intervals[i][0] <= end {
		start = minInt(start, intervals[i][0])
		end = maxInt(end, intervals[i][1])
		i++
	}
	ans = append(ans, []int{start, end})
	for i < n {
		ans = append(ans, intervals[i])
		i++
	}
	return ans
}
