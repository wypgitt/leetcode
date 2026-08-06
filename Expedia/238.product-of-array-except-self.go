package leetcode

// ProductExceptSelf238 writes prefix products into ans, then multiplies by a
// right-to-left suffix product. This avoids division and handles zeros naturally.
//
// Time: O(n). Extra space: O(1) excluding output.
func ProductExceptSelf238(nums []int) []int {
	ans := make([]int, len(nums))
	prefix := 1
	for i, x := range nums {
		ans[i] = prefix
		prefix *= x
	}
	suffix := 1
	for i := len(nums) - 1; i >= 0; i-- {
		ans[i] *= suffix
		suffix *= nums[i]
	}
	return ans
}
