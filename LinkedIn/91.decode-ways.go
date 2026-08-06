package leetcode

// NumDecodings91 keeps only dp[i-2] and dp[i-1]. Single-character decodes are
// valid for '1'..'9'; two-character decodes are valid for "10".."26".
//
// Time: O(n). Space: O(1).
func NumDecodings91(s string) int {
	if len(s) == 0 || s[0] == '0' {
		return 0
	}
	two, one := 1, 1
	for i := 1; i < len(s); i++ {
		cur := 0
		if s[i] != '0' {
			cur += one
		}
		v := int(s[i-1]-'0')*10 + int(s[i]-'0')
		if v >= 10 && v <= 26 {
			cur += two
		}
		two, one = one, cur
	}
	return one
}
