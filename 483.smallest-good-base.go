package leetcode

//
// @lc app=leetcode id=483 lang=golang
//
// [483] Smallest Good Base
//
// Notes
// A good base k represents n as 1 + k + ... + k^p. Try the largest possible
// power p first, because more digits imply a smaller base. For each p, binary
// search the base and evaluate the geometric sum with early stopping. Time:
// O(log^2 n). Space: O(1).
//
// @lc code=start

import "strconv"

func SmallestGoodBase483(n string) string {
	number, _ := strconv.ParseInt(n, 10, 64)
	maxPower := bitLength483(number) - 1

	for power := maxPower; power > 1; power-- {
		left, right := int64(2), number-1
		for left <= right {
			middle := left + (right-left)/2
			currentSum := geometricSum483(middle, power, number)
			if currentSum == number {
				return strconv.FormatInt(middle, 10)
			}
			if currentSum < number {
				left = middle + 1
			} else {
				right = middle - 1
			}
		}
	}

	return strconv.FormatInt(number-1, 10)
}

func geometricSum483(base int64, power int, limit int64) int64 {
	total := int64(1)
	term := int64(1)
	for i := 0; i < power; i++ {
		if term > limit/base {
			return limit + 1
		}
		term *= base
		total += term
		if total > limit {
			break
		}
	}
	return total
}

func bitLength483(value int64) int {
	length := 0
	for value > 0 {
		length++
		value >>= 1
	}
	return length
}

// @lc code=end
