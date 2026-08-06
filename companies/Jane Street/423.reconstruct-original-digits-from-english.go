package leetcode

import "strings"

// OriginalDigits423 counts unique identifying letters for digits: z, w, u, x,
// and g identify 0,2,4,6,8 first; the remaining digits are derived after those
// counts are known.
//
// Go data structure note: a fixed [26]int array is faster and simpler than a
// map because the alphabet is fixed lowercase English letters.
//
// Time: O(n). Space: O(1), excluding output.
func OriginalDigits423(s string) string {
	count := [26]int{}
	for i := 0; i < len(s); i++ {
		count[s[i]-'a']++
	}
	digit := [10]int{}
	digit[0] = count['z'-'a']
	digit[2] = count['w'-'a']
	digit[4] = count['u'-'a']
	digit[6] = count['x'-'a']
	digit[8] = count['g'-'a']
	digit[3] = count['h'-'a'] - digit[8]
	digit[5] = count['f'-'a'] - digit[4]
	digit[7] = count['s'-'a'] - digit[6]
	digit[1] = count['o'-'a'] - digit[0] - digit[2] - digit[4]
	digit[9] = count['i'-'a'] - digit[5] - digit[6] - digit[8]

	var b strings.Builder
	for i, c := range digit {
		for ; c > 0; c-- {
			b.WriteByte(byte('0' + i))
		}
	}
	return b.String()
}
