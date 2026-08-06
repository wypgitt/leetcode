package leetcode

// ShiftingLetters848 scans right-to-left with a suffix shift modulo 26. Each
// character is shifted once by the total of all shifts affecting it.
//
// Time: O(n). Space: O(n) for the output byte slice.
func ShiftingLetters848(s string, shifts []int) string {
	chars := []byte(s)
	total := 0
	for i := len(s) - 1; i >= 0; i-- {
		total = (total + shifts[i]) % 26
		chars[i] = byte((int(chars[i]-'a')+total)%26 + 'a')
	}
	return string(chars)
}
