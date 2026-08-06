package leetcode

// Reverse7 reverses the absolute value digit by digit, restores the sign, and
// rejects results outside the signed 32-bit range.
//
// Time: O(log10 |x|). Space: O(1).
func Reverse7(x int) int {
	sign := 1
	if x < 0 {
		sign = -1
		x = -x
	}
	ans := 0
	for x > 0 {
		ans = ans*10 + x%10
		x /= 10
	}
	ans *= sign
	if ans < -1<<31 || ans > 1<<31-1 {
		return 0
	}
	return ans
}
