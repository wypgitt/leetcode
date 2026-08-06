package leetcode

import (
	"strconv"
	"strings"
)

// FractionToDecimal166 performs long division and maps each remainder to the
// output position where it first appeared. Repeating a remainder means the digits
// from that position repeat, so parentheses are inserted there.
//
// Time: O(period length). Space: O(period length).
func FractionToDecimal166(numerator int, denominator int) string {
	if numerator == 0 {
		return "0"
	}
	sign := ""
	if (numerator < 0) != (denominator < 0) {
		sign = "-"
	}
	n, d := numerator, denominator
	if n < 0 {
		n = -n
	}
	if d < 0 {
		d = -d
	}
	integer := n / d
	rem := n % d
	if rem == 0 {
		return sign + strconv.Itoa(integer)
	}
	out := []string{sign + strconv.Itoa(integer), "."}
	seen := map[int]int{}
	for rem != 0 {
		if idx, ok := seen[rem]; ok {
			out = append(out, "")
			copy(out[idx+1:], out[idx:])
			out[idx] = "("
			out = append(out, ")")
			break
		}
		seen[rem] = len(out)
		rem *= 10
		out = append(out, strconv.Itoa(rem/d))
		rem %= d
	}
	return strings.Join(out, "")
}
