package main

func reverseParentheses(s string) string {
	stack := []byte{}
	for i := 0; i < len(s); i++ {
		if s[i] != ')' {
			stack = append(stack, s[i])
			continue
		}

		reversed := []byte{}
		for stack[len(stack)-1] != '(' {
			reversed = append(reversed, stack[len(stack)-1])
			stack = stack[:len(stack)-1]
		}
		stack = stack[:len(stack)-1]
		stack = append(stack, reversed...)
	}
	return string(stack)
}

