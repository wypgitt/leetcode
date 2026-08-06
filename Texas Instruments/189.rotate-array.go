package leetcode

// Rotate189 rotates right by k using three reversals: reverse whole array,
// reverse the first k values, then reverse the remainder.
//
// Time: O(n). Space: O(1).
func Rotate189(nums []int, k int) {
	n := len(nums)
	if n == 0 {
		return
	}
	k %= n
	rev := func(l, r int) {
		for l < r {
			nums[l], nums[r] = nums[r], nums[l]
			l++
			r--
		}
	}
	rev(0, n-1)
	rev(0, k-1)
	rev(k, n-1)
}
