package leetcode

// MinSubArrayLen209 uses a sliding window because all numbers are positive. The
// right side expands the sum; while sum >= target, shrink left and record the
// shortest valid length.
//
// Time: O(n). Space: O(1).
func MinSubArrayLen209(target int, nums []int) int {
	left, total, best := 0, 0, len(nums)+1
	for right, x := range nums {
		total += x
		for total >= target {
			best = minInt(best, right-left+1)
			total -= nums[left]
			left++
		}
	}
	if best == len(nums)+1 {
		return 0
	}
	return best
}
