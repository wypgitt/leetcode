package leetcode

import "strings"

// MaskPII831 applies separate normalization rules for email and phone numbers.
// Emails are lowercased and keep first/last name characters. Phone numbers strip
// punctuation, keep the last four digits, and mask the optional country code.
//
// Time: O(n). Space: O(n) for normalized output.
func MaskPII831(s string) string {
	if strings.Contains(s, "@") {
		parts := strings.Split(strings.ToLower(s), "@")
		name, domain := parts[0], parts[1]
		return string(name[0]) + "*****" + string(name[len(name)-1]) + "@" + domain
	}
	digits := []byte{}
	for i := 0; i < len(s); i++ {
		if s[i] >= '0' && s[i] <= '9' {
			digits = append(digits, s[i])
		}
	}
	local := "***-***-" + string(digits[len(digits)-4:])
	countryLen := len(digits) - 10
	if countryLen == 0 {
		return local
	}
	return "+" + strings.Repeat("*", countryLen) + "-" + local
}
