package leetcode

// IsOneEditDistance161 compares the first mismatch. Equal lengths require the
// suffixes after that mismatch to match after one replacement; unequal lengths
// require the shorter suffix to match after skipping one char in the longer
// string. Identical strings are zero edits, not one.
//
// Time: O(n). Space: O(1).
func IsOneEditDistance161(s string, t string) bool {
	if absInt(len(s)-len(t)) > 1 {
		return false
	}
	if len(s) > len(t) {
		s, t = t, s
	}
	for i := 0; i < len(s); i++ {
		if s[i] != t[i] {
			if len(s) == len(t) {
				return s[i+1:] == t[i+1:]
			}
			return s[i:] == t[i+1:]
		}
	}
	return len(t)-len(s) == 1
}
