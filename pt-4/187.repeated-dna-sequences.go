package leetcode

// FindRepeatedDnaSequences187 records every length-10 window seen once and every
// window seen more than once. Hash sets keep membership checks O(1) on average.
//
// Time: O(n) windows, with constant window length 10. Space: O(n).
func FindRepeatedDnaSequences187(s string) []string {
	seen := map[string]bool{}
	repeated := map[string]bool{}
	for i := 0; i+10 <= len(s); i++ {
		w := s[i : i+10]
		if seen[w] {
			repeated[w] = true
		} else {
			seen[w] = true
		}
	}
	ans := []string{}
	for w := range repeated {
		ans = append(ans, w)
	}
	return ans
}
