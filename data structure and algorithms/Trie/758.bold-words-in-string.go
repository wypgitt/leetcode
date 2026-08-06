package leetcode

import "strings"

// BoldWords758 marks every character covered by any word occurrence, then wraps
// each maximal consecutive marked segment once. This automatically merges
// overlapping and adjacent intervals.
//
// Time: O(sum of search work + n). Space: O(n).
func BoldWords758(words []string, s string) string {
	bold := make([]bool, len(s))
	for _, word := range words {
		start := strings.Index(s, word)
		for start != -1 {
			for i := start; i < start+len(word); i++ {
				bold[i] = true
			}
			next := strings.Index(s[start+1:], word)
			if next == -1 {
				start = -1
			} else {
				start += 1 + next
			}
		}
	}
	var b strings.Builder
	for i := 0; i < len(s); {
		if !bold[i] {
			b.WriteByte(s[i])
			i++
		} else {
			b.WriteString("<b>")
			for i < len(s) && bold[i] {
				b.WriteByte(s[i])
				i++
			}
			b.WriteString("</b>")
		}
	}
	return b.String()
}
