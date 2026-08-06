package leetcode

// MaxRotateFunction396 computes F(0), then updates each rotation in O(1):
// F(k) = F(k-1) + sum(nums) - n*nums[n-k]. The last term is the value moved
// from the end to index 0 by the kth right rotation.
//
// Time: O(n). Space: O(1).
func MaxRotateFunction396(nums []int) int {
	total, cur := 0, 0
	for i, x := range nums {
		total += x
		cur += i * x
	}
	best := cur
	n := len(nums)
	for k := 1; k < n; k++ {
		cur = cur + total - n*nums[n-k]
		best = maxInt(best, cur)
	}
	return best
}
