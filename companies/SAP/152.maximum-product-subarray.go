package leetcode

// MaxProduct152 tracks both max and min products ending at the current index.
// A negative number swaps their roles, because multiplying by it turns the most
// negative product into a candidate maximum.
//
// Time: O(n). Space: O(1).
func MaxProduct152(nums []int) int {
	curMax, curMin, ans := nums[0], nums[0], nums[0]
	for _, x := range nums[1:] {
		if x < 0 {
			curMax, curMin = curMin, curMax
		}
		curMax = maxInt(x, curMax*x)
		curMin = minInt(x, curMin*x)
		ans = maxInt(ans, curMax)
	}
	return ans
}
