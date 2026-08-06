package leetcode

// Divide29 performs binary long division by repeatedly subtracting the largest
// doubled divisor chunk that fits. It works with absolute values, restores sign,
// and handles the one 32-bit overflow case.
//
// Time: O(log^2 N) in this simple doubling form. Space: O(1).
func Divide29(dividend int, divisor int) int {
	const intMax = 1<<31 - 1
	const intMin = -1 << 31
	if dividend == intMin && divisor == -1 {
		return intMax
	}
	negative := (dividend < 0) != (divisor < 0)
	a, b := dividend, divisor
	if a < 0 {
		a = -a
	}
	if b < 0 {
		b = -b
	}
	q := 0
	for a >= b {
		chunk, multiple := b, 1
		for a >= chunk<<1 {
			chunk <<= 1
			multiple <<= 1
		}
		a -= chunk
		q += multiple
	}
	if negative {
		return -q
	}
	return q
}
