package leetcode

// MyPow50 uses binary exponentiation. Each loop square represents the next power
// of two; when the current exponent bit is 1, that power contributes to answer.
// Negative exponents invert x first.
//
// Time: O(log |n|). Space: O(1).
func MyPow50(x float64, n int) float64 {
	if n < 0 {
		x = 1 / x
		n = -n
	}
	ans := 1.0
	for n > 0 {
		if n&1 == 1 {
			ans *= x
		}
		x *= x
		n >>= 1
	}
	return ans
}
