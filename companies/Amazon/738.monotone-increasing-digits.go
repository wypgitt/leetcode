package leetcode

import "strconv"

// MonotoneIncreasingDigits738 scans digits right-to-left. When a descent is
// found, decrement the left digit and later set every following digit to 9. The
// reverse scan handles cascades such as 332 -> 299.
//
// Time: O(d). Space: O(d), where d is digit count.
func MonotoneIncreasingDigits738(n int) int {
	digits := []byte(strconv.Itoa(n))
	marker := len(digits)
	for i := len(digits) - 1; i > 0; i-- {
		if digits[i-1] > digits[i] {
			digits[i-1]--
			marker = i
		}
	}
	for i := marker; i < len(digits); i++ {
		digits[i] = '9'
	}
	ans, _ := strconv.Atoi(string(digits))
	return ans
}
