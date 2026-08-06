package leetcode

import (
	"fmt"
	"strconv"
	"strings"
)

// ComplexNumberMultiply537 parses a+bi pairs and applies
// (a+bi)(c+di) = (ac-bd) + (ad+bc)i.
//
// Time: O(len(num1)+len(num2)). Space: O(1).
func ComplexNumberMultiply537(num1 string, num2 string) string {
	parse := func(num string) (int, int) {
		parts := strings.Split(strings.TrimSuffix(num, "i"), "+")
		real, _ := strconv.Atoi(parts[0])
		imag, _ := strconv.Atoi(parts[1])
		return real, imag
	}
	a, b := parse(num1)
	c, d := parse(num2)
	return fmt.Sprintf("%d+%di", a*c-b*d, a*d+b*c)
}
