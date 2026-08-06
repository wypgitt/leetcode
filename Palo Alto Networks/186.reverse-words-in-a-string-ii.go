package leetcode

// ReverseWords186 reverses the whole byte slice, then reverses each word in
// place. The two reversals put words in reverse order while preserving characters
// inside each word.
//
// Time: O(n). Space: O(1).
func ReverseWords186(s []byte) {
	rev := func(l, r int) {
		for l < r {
			s[l], s[r] = s[r], s[l]
			l++
			r--
		}
	}
	rev(0, len(s)-1)
	start := 0
	for i := 0; i <= len(s); i++ {
		if i == len(s) || s[i] == ' ' {
			rev(start, i-1)
			start = i + 1
		}
	}
}
