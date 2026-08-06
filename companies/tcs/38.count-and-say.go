package leetcode

import (
	"strconv"
	"strings"
)

// CountAndSay38 iteratively run-length encodes the previous term: count adjacent
// equal digits and append count followed by digit.
//
// Time: O(total generated length). Space: O(current term length).
func CountAndSay38(n int) string {
	term := "1"
	for step := 1; step < n; step++ {
		var b strings.Builder
		for i := 0; i < len(term); {
			j := i
			for j < len(term) && term[j] == term[i] {
				j++
			}
			b.WriteString(strconv.Itoa(j - i))
			b.WriteByte(term[i])
			i = j
		}
		term = b.String()
	}
	return term
}
