package leetcode

// Calculate227 scans numbers and operators once. Addition/subtraction push signed
// values; multiplication/division immediately combine with the previous stack
// value to enforce precedence. Go integer division truncates toward zero.
//
// Time: O(n). Space: O(n).
func Calculate227(s string) int {
	stack := []int{}
	num := 0
	op := byte('+')
	for i := 0; i <= len(s); i++ {
		ch := byte('+')
		if i < len(s) {
			ch = s[i]
		}
		if ch == ' ' {
			continue
		}
		if ch >= '0' && ch <= '9' {
			num = num*10 + int(ch-'0')
			continue
		}
		if op == '+' {
			stack = append(stack, num)
		} else if op == '-' {
			stack = append(stack, -num)
		} else if op == '*' {
			stack[len(stack)-1] *= num
		} else {
			stack[len(stack)-1] /= num
		}
		op = ch
		num = 0
	}
	sum := 0
	for _, v := range stack {
		sum += v
	}
	return sum
}
