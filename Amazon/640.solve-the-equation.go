package leetcode

import (
	"strconv"
	"strings"
)

// SolveEquation640 parses each side as coeff*x + constant, moves x terms left
// and constants right, then solves coeff*x = constant or detects no/infinite
// solutions.
//
// Time: O(n). Space: O(1).
func SolveEquation640(equation string) string {
	parse := func(side string) (int, int) {
		coeff, constant := 0, 0
		i, sign := 0, 1
		for i < len(side) {
			if side[i] == '+' {
				sign = 1
				i++
			} else if side[i] == '-' {
				sign = -1
				i++
			} else {
				j := i
				for j < len(side) && side[j] >= '0' && side[j] <= '9' {
					j++
				}
				num := 1
				if j > i {
					num, _ = strconv.Atoi(side[i:j])
				}
				if j < len(side) && side[j] == 'x' {
					coeff += sign * num
					j++
				} else {
					constant += sign * num
				}
				i = j
			}
		}
		return coeff, constant
	}
	parts := strings.Split(equation, "=")
	lx, lc := parse(parts[0])
	rx, rc := parse(parts[1])
	coeff := lx - rx
	constant := rc - lc
	if coeff == 0 {
		if constant == 0 {
			return "Infinite solutions"
		}
		return "No solution"
	}
	return "x=" + strconv.Itoa(constant/coeff)
}
