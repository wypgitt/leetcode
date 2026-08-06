package leetcode

// MaxSubArray53 is Kadane's algorithm: the best subarray ending here either
// extends the previous best-ending-here or starts fresh at the current number.
//
// Time: O(n). Space: O(1).
func MaxSubArray53(nums []int) int {
	cur, best := nums[0], nums[0]
	for _, x := range nums[1:] {
		cur = maxInt(x, cur+x)
		best = maxInt(best, cur)
	}
	return best
}
