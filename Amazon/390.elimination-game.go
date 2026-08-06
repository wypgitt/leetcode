package leetcode

// LastRemaining390 keeps the remaining arithmetic progression compressed as
// head, step, count, and direction. The head advances on every left-to-right
// pass and on right-to-left passes with an odd count.
//
// Time: O(log n), because remaining halves each round. Space: O(1).
func LastRemaining390(n int) int {
	head, step, remaining := 1, 1, n
	leftToRight := true
	for remaining > 1 {
		if leftToRight || remaining%2 == 1 {
			head += step
		}
		remaining /= 2
		step *= 2
		leftToRight = !leftToRight
	}
	return head
}
