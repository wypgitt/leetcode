package leetcode

import "strconv"

// EvalRPN150 evaluates tokens with an integer stack. Operators pop b then a and
// push a op b. Division truncates toward zero, matching LeetCode and Go integer
// division semantics.
//
// Time: O(n). Space: O(n).
func EvalRPN150(tokens []string) int {
	st := []int{}
	for _, tok := range tokens {
		switch tok {
		case "+", "-", "*", "/":
			b := st[len(st)-1]
			a := st[len(st)-2]
			st = st[:len(st)-2]
			if tok == "+" {
				st = append(st, a+b)
			} else if tok == "-" {
				st = append(st, a-b)
			} else if tok == "*" {
				st = append(st, a*b)
			} else {
				st = append(st, a/b)
			}
		default:
			v, _ := strconv.Atoi(tok)
			st = append(st, v)
		}
	}
	return st[len(st)-1]
}
