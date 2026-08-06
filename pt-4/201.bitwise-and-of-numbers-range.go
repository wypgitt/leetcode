package leetcode

// RangeBitwiseAnd201 shifts left and right until their common prefix is equal.
// Any differing lower bit flips within the range and becomes zero in the AND.
//
// Time: O(log n). Space: O(1).
func RangeBitwiseAnd201(left int, right int) int {
	shift := 0
	for left < right {
		left >>= 1
		right >>= 1
		shift++
	}
	return left << shift
}
