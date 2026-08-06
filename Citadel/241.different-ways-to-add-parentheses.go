package leetcode

import "strconv"

// DiffWaysToCompute241 recursively splits on each operator and combines every
// result from the left expression with every result from the right expression.
// Memoization by substring avoids recomputing the same expression range.
//
// Time: Catalan-sized output dominates. Space: O(number of substrings + output).
func DiffWaysToCompute241(expression string) []int {
	memo := map[string][]int{}
	var solve func(string) []int
	solve = func(expr string) []int {
		if v, ok := memo[expr]; ok {
			return v
		}
		res := []int{}
		for i := 0; i < len(expr); i++ {
			ch := expr[i]
			if ch == '+' || ch == '-' || ch == '*' {
				for _, a := range solve(expr[:i]) {
					for _, b := range solve(expr[i+1:]) {
						if ch == '+' {
							res = append(res, a+b)
						} else if ch == '-' {
							res = append(res, a-b)
						} else {
							res = append(res, a*b)
						}
					}
				}
			}
		}
		if len(res) == 0 {
			v, _ := strconv.Atoi(expr)
			res = append(res, v)
		}
		memo[expr] = res
		return res
	}
	return solve(expression)
}
