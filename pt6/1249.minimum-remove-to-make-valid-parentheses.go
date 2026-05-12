package main

func minRemoveToMakeValid(s string) string {
	stack := []int{}
	remove := map[int]bool{}

	for i := 0; i < len(s); i++ {
		if s[i] == '(' {
			stack = append(stack, i)
		} else if s[i] == ')' {
			if len(stack) > 0 {
				stack = stack[:len(stack)-1]
			} else {
				remove[i] = true
			}
		}
	}

	for _, idx := range stack {
		remove[idx] = true
	}

	ans := make([]byte, 0, len(s))
	for i := 0; i < len(s); i++ {
		if !remove[i] {
			ans = append(ans, s[i])
		}
	}
	return string(ans)
}

/*
Explanation

Use a stack of indices for unmatched opening parentheses. A closing parenthesis
matches the most recent opening parenthesis if one exists; otherwise that
closing parenthesis must be removed. After the scan, any indices left in the
stack are unmatched openings and must also be removed.

The stack is the correct data structure because parentheses match in
last-opened, first-closed order.

Edge cases: extra ')' at the front; extra '(' at the end; letters are copied
unchanged.

Time complexity: O(n).
Space complexity: O(n).
*/
