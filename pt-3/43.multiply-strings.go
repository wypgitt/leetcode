package leetcode

import "strings"

// Multiply43 simulates grade-school multiplication into an m+n digit array.
// Each pair of digits contributes to positions i+j and i+j+1, allowing carries
// without converting the whole input to an integer.
//
// Time: O(m*n). Space: O(m+n).
func Multiply43(num1 string, num2 string) string {
	if num1 == "0" || num2 == "0" {
		return "0"
	}
	m, n := len(num1), len(num2)
	res := make([]int, m+n)
	for i := m - 1; i >= 0; i-- {
		for j := n - 1; j >= 0; j-- {
			p := int(num1[i]-'0') * int(num2[j]-'0')
			total := p + res[i+j+1]
			res[i+j+1] = total % 10
			res[i+j] += total / 10
		}
	}
	start := 0
	for start < len(res) && res[start] == 0 {
		start++
	}
	var b strings.Builder
	for ; start < len(res); start++ {
		b.WriteByte(byte(res[start] + '0'))
	}
	return b.String()
}
