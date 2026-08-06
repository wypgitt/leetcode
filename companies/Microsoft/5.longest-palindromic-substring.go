package leetcode

// LongestPalindrome5 expands around every odd and even center. This checks all
// palindromic candidates without an O(n^2) DP table.
//
// Time: O(n^2). Space: O(1).
func LongestPalindrome5(s string) string {
	if len(s) == 0 {
		return ""
	}
	expand := func(l, r int) (int, int) {
		for l >= 0 && r < len(s) && s[l] == s[r] {
			l--
			r++
		}
		return l + 1, r - 1
	}
	bestL, bestR := 0, 0
	for i := 0; i < len(s); i++ {
		l, r := expand(i, i)
		if r-l > bestR-bestL {
			bestL, bestR = l, r
		}
		l, r = expand(i, i+1)
		if r-l > bestR-bestL {
			bestL, bestR = l, r
		}
	}
	return s[bestL : bestR+1]
}
