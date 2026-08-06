package leetcode

// MyAtoi8 parses optional spaces, optional sign, then consecutive digits. The
// value is clamped during construction to the signed 32-bit range, which is the
// important fixed-width-integer concern in Go.
//
// Time: O(n) over the parsed prefix. Space: O(1).
func MyAtoi8(s string) int {
	const intMax = 1<<31 - 1
	const intMin = -1 << 31
	i, n := 0, len(s)
	for i < n && s[i] == ' ' {
		i++
	}
	sign := 1
	if i < n && (s[i] == '+' || s[i] == '-') {
		if s[i] == '-' {
			sign = -1
		}
		i++
	}
	value := 0
	for i < n && s[i] >= '0' && s[i] <= '9' {
		value = value*10 + int(s[i]-'0')
		if sign == 1 && value >= intMax {
			return intMax
		}
		if sign == -1 && -value <= intMin {
			return intMin
		}
		i++
	}
	return sign * value
}
