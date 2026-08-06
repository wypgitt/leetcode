package leetcode

// Rob198 keeps rolling DP: prev1 is best through previous house, prev2 through
// the house before that. For each amount, choose skip current or rob current.
//
// Time: O(n). Space: O(1).
func Rob198(nums []int) int {
	prev2, prev1 := 0, 0
	for _, x := range nums {
		prev2, prev1 = prev1, maxInt(prev1, prev2+x)
	}
	return prev1
}
