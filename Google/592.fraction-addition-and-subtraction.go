package leetcode

import (
	"fmt"
	"strconv"
)

// FractionAddition592 scans signed fractions and keeps a reduced running total.
// Adding n/d to a/b gives (a*d+n*b)/(b*d), then gcd reduction keeps values small.
//
// Time: O(t log V) for t fractions. Space: O(1).
func FractionAddition592(expression string) string {
	numerator, denominator := 0, 1
	for i := 0; i < len(expression); {
		sign := 1
		if expression[i] == '+' || expression[i] == '-' {
			if expression[i] == '-' {
				sign = -1
			}
			i++
		}
		j := i
		for expression[j] != '/' {
			j++
		}
		n, _ := strconv.Atoi(expression[i:j])
		n *= sign
		i = j + 1
		j = i
		for j < len(expression) && expression[j] >= '0' && expression[j] <= '9' {
			j++
		}
		d, _ := strconv.Atoi(expression[i:j])
		numerator = numerator*d + n*denominator
		denominator *= d
		g := gcdInt(absInt(numerator), denominator)
		numerator /= g
		denominator /= g
		i = j
	}
	return fmt.Sprintf("%d/%d", numerator, denominator)
}

func gcdInt(a, b int) int {
	for b != 0 {
		a, b = b, a%b
	}
	if a == 0 {
		return 1
	}
	return a
}
