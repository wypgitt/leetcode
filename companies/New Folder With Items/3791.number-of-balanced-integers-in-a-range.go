package leetcode

//
// @lc app=leetcode id=3791 lang=golang
//
// [3791] Number of Balanced Integers in a Range
//
// Notes
// Count balanced values up to x with digit DP, then subtract prefix counts.
// The DP state is position, alternating digit-sum difference, and tightness;
// leading zeroes are disallowed by forcing the first digit to be at least 1.
// Go uses a map keyed by a small struct to memoize states. Time: O(D^2*10) per
// bound in practice. Space: O(D^2).
//
// @lc code=start

import "strconv"

type dpKey3791 struct {
	index int
	diff  int
	tight bool
}

func CountBalanced3791(low int, high int) int {
	countFixedLength := func(boundDigits []int) int {
		length := len(boundDigits)
		memo := map[dpKey3791]int{}

		var dfs func(index, diff int, tight bool) int
		dfs = func(index, diff int, tight bool) int {
			if index == length {
				if diff == 0 {
					return 1
				}
				return 0
			}

			key := dpKey3791{index: index, diff: diff, tight: tight}
			if value, ok := memo[key]; ok {
				return value
			}

			upper := 9
			if tight {
				upper = boundDigits[index]
			}
			lower := 0
			if index == 0 {
				lower = 1
			}

			total := 0
			for digit := lower; digit <= upper; digit++ {
				nextDiff := diff - digit
				if index%2 == 0 {
					nextDiff = diff + digit
				}
				total += dfs(index+1, nextDiff, tight && digit == upper)
			}
			memo[key] = total
			return total
		}

		return dfs(0, 0, true)
	}

	countUpTo := func(limit int) int {
		if limit < 10 {
			return 0
		}

		text := strconv.Itoa(limit)
		digits := make([]int, len(text))
		for i := range text {
			digits[i] = int(text[i] - '0')
		}

		total := 0
		for length := 2; length < len(digits); length++ {
			bound := make([]int, length)
			for i := range bound {
				bound[i] = 9
			}
			total += countFixedLength(bound)
		}
		total += countFixedLength(digits)
		return total
	}

	return countUpTo(high) - countUpTo(low-1)
}

// @lc code=end
