package leetcode

import "strconv"

// Deserialize385 parses a serialized NestedInteger using a stack of open lists.
// '[' opens a new NestedInteger list. A number is materialized only when a comma
// or ']' ends its token, which naturally handles negative and multi-digit values.
//
// Go data structure note: []NestedInteger is used as a stack. The top slice
// element is the list currently receiving children; Add mutates that element.
//
// Time: O(n), one scan of s. Space: O(depth) auxiliary stack, excluding output.
func Deserialize385(s string) NestedInteger {
	if len(s) == 0 {
		return NewNestedInteger()
	}
	if s[0] != '[' {
		v, _ := strconv.Atoi(s)
		return NewNestedIntegerWithValue(v)
	}

	stack := []NestedInteger{}
	numberStart := -1
	for i := 0; i < len(s); i++ {
		switch s[i] {
		case '[':
			stack = append(stack, NewNestedInteger())
		case ']':
			if numberStart != -1 {
				v, _ := strconv.Atoi(s[numberStart:i])
				stack[len(stack)-1].Add(NewNestedIntegerWithValue(v))
				numberStart = -1
			}
			finished := stack[len(stack)-1]
			stack = stack[:len(stack)-1]
			if len(stack) == 0 {
				return finished
			}
			stack[len(stack)-1].Add(finished)
		case ',':
			if numberStart != -1 {
				v, _ := strconv.Atoi(s[numberStart:i])
				stack[len(stack)-1].Add(NewNestedIntegerWithValue(v))
				numberStart = -1
			}
		default:
			if numberStart == -1 {
				numberStart = i
			}
		}
	}
	return NewNestedInteger()
}
