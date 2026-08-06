package leetcode

// FindSubstringInWraproundString467 keeps, for each ending character, the
// longest valid wraparound run ending there. A longest run of length L ending at
// c contributes exactly L distinct substrings ending at c.
//
// Go data structure note: [26]int is a fixed-size DP table for lowercase
// letters, giving constant auxiliary space.
//
// Time: O(n). Space: O(1).
func FindSubstringInWraproundString467(s string) int {
	best := [26]int{}
	run := 0
	prev := byte(0)
	for i := 0; i < len(s); i++ {
		ch := s[i]
		if i > 0 && int(ch-prev+26)%26 == 1 {
			run++
		} else {
			run = 1
		}
		idx := ch - 'a'
		if run > best[idx] {
			best[idx] = run
		}
		prev = ch
	}
	ans := 0
	for _, v := range best {
		ans += v
	}
	return ans
}
