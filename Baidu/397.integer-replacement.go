package leetcode

//
// @lc app=leetcode id=397 lang=golang
//
// [397] Integer Replacement
//
// Notes
// Repeatedly halve even numbers. For odd numbers, decrement when n is 3 or ends
// in binary 01; otherwise increment to create more trailing zero bits before
// halving. int64 avoids overflow when incrementing a large int. Time: O(log n).
// Space: O(1).
//
// @lc code=start

func IntegerReplacement397(n int) int {
	value := int64(n)
	steps := 0
	for value != 1 {
		if value%2 == 0 {
			value /= 2
		} else if value == 3 || value&3 == 1 {
			value--
		} else {
			value++
		}
		steps++
	}
	return steps
}

// @lc code=end
