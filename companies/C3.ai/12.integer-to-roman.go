package leetcode

import "strings"

// IntToRoman12 greedily appends the largest Roman symbol, including subtractive
// forms like CM and IV. Because the value table is complete and descending, each
// place group is represented optimally.
//
// Time/space: O(1), since num is constrained to 1..3999.
func IntToRoman12(num int) string {
	values := []struct {
		v int
		s string
	}{{1000, "M"}, {900, "CM"}, {500, "D"}, {400, "CD"}, {100, "C"}, {90, "XC"}, {50, "L"}, {40, "XL"}, {10, "X"}, {9, "IX"}, {5, "V"}, {4, "IV"}, {1, "I"}}
	var b strings.Builder
	for _, p := range values {
		for num >= p.v {
			b.WriteString(p.s)
			num -= p.v
		}
	}
	return b.String()
}
