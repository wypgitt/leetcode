package leetcode

// TrailingZeroes172 counts factors of 5 in n!, including repeated factors from
// 25, 125, etc. Factors of 2 are more abundant and do not limit trailing zeros.
//
// Time: O(log_5 n). Space: O(1).
func TrailingZeroes172(n int) int {
	count := 0
	for n > 0 {
		n /= 5
		count += n
	}
	return count
}
