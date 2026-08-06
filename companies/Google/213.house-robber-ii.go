package leetcode

// Rob213 breaks the circle by excluding either the first house or the last house,
// then applies linear House Robber DP to both ranges and takes the better result.
//
// Time: O(n). Space: O(1).
func Rob213(nums []int) int {
	if len(nums) == 1 {
		return nums[0]
	}
	robLine := func(arr []int) int {
		prev2, prev1 := 0, 0
		for _, x := range arr {
			prev2, prev1 = prev1, maxInt(prev1, prev2+x)
		}
		return prev1
	}
	return maxInt(robLine(nums[:len(nums)-1]), robLine(nums[1:]))
}
