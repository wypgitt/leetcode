package main

import "strings"

func removeDuplicates(s string, k int) string {
	type run struct {
		ch    byte
		count int
	}

	stack := make([]run, 0, len(s))
	for i := 0; i < len(s); i++ {
		ch := s[i]
		if len(stack) > 0 && stack[len(stack)-1].ch == ch {
			stack[len(stack)-1].count++
		} else {
			stack = append(stack, run{ch: ch, count: 1})
		}

		if stack[len(stack)-1].count == k {
			stack = stack[:len(stack)-1]
		}
	}

	var builder strings.Builder
	builder.Grow(len(s))
	for _, item := range stack {
		for i := 0; i < item.count; i++ {
			builder.WriteByte(item.ch)
		}
	}
	return builder.String()
}

/*
Explanation

The stack stores compressed runs: character plus how many consecutive copies
survive so far. For each byte, either extend the top run or push a new run. If
the top run reaches k, pop it immediately.

This stack is ideal because deletions only affect the newest surviving run.
When a group is removed, the previous stack entry becomes adjacent to future
characters automatically, which handles chained deletions without rescanning.

Go detail: strings.Builder constructs the final string efficiently instead of
repeated string concatenation.

Edge cases: k == 1 removes everything; alternating characters never hit k;
after one pop, later characters can merge with the run revealed underneath.

Time complexity: O(n).
Space complexity: O(n) in the worst case for the stack.
*/
