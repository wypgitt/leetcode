package leetcode

// ParseTernary439 scans from right to left because ternary expressions are
// right-associative. When the stack top is '?', the current byte is the
// condition and the already-collapsed true/false branches are on the stack.
//
// Go data structure note: []byte is used as a stack of unresolved tokens and
// resolved one-character expressions.
//
// Time: O(n). Space: O(n).
func ParseTernary439(expression string) string {
	stack := []byte{}
	for i := len(expression) - 1; i >= 0; i-- {
		ch := expression[i]
		if len(stack) > 0 && stack[len(stack)-1] == '?' {
			stack = stack[:len(stack)-1]
			trueExpr := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			stack = stack[:len(stack)-1] // ':'
			falseExpr := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			if ch == 'T' {
				stack = append(stack, trueExpr)
			} else {
				stack = append(stack, falseExpr)
			}
		} else {
			stack = append(stack, ch)
		}
	}
	return string(stack[len(stack)-1])
}
