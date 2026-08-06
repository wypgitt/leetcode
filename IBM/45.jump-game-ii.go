package leetcode

// Jump45 compresses BFS levels over indices. currentEnd is the farthest index
// reachable with the current jump count; farthest is the best reach found while
// scanning that level. Reaching currentEnd forces one more jump.
//
// Time: O(n). Space: O(1).
func Jump45(nums []int) int {
	jumps, end, farthest := 0, 0, 0
	for i := 0; i < len(nums)-1; i++ {
		farthest = maxInt(farthest, i+nums[i])
		if i == end {
			jumps++
			end = farthest
		}
	}
	return jumps
}
