package leetcode

// SingleNumber137 tracks bits seen once and twice modulo three. When a bit would
// appear for the third time, it is cleared from both masks. This avoids per-bit
// counting and works in constant space.
//
// Time: O(n). Space: O(1).
func SingleNumber137(nums []int) int {
	ones, twos := 0, 0
	for _, x := range nums {
		ones = (ones ^ x) &^ twos
		twos = (twos ^ x) &^ ones
	}
	return ones
}
