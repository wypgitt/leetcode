package leetcode

// AmbiguousCoordinates816 removes outer parentheses, splits the digits into x/y
// parts, generates every valid decimal form for each side, and combines them.
// Leading zeros are only allowed for the number 0; decimal fractions cannot end
// in zero.
//
// Time: O(n^3) including output construction. Space: O(output).
func AmbiguousCoordinates816(s string) []string {
	digits := s[1 : len(s)-1]
	forms := func(part string) []string {
		if len(part) == 1 {
			return []string{part}
		}
		ans := []string{}
		if part[0] != '0' {
			ans = append(ans, part)
		}
		for i := 1; i < len(part); i++ {
			left, right := part[:i], part[i:]
			validLeft := left == "0" || left[0] != '0'
			if validLeft && right[len(right)-1] != '0' {
				ans = append(ans, left+"."+right)
			}
		}
		return ans
	}
	ans := []string{}
	for i := 1; i < len(digits); i++ {
		for _, left := range forms(digits[:i]) {
			for _, right := range forms(digits[i:]) {
				ans = append(ans, "("+left+", "+right+")")
			}
		}
	}
	return ans
}
