package leetcode

//
// @lc app=leetcode id=3895 lang=golang
//
// [3895] Count Digit Appearances
//
// Notes
// Convert each number to decimal text and count occurrences of the requested
// digit, matching the Python implementation directly. Time is proportional to
// the total number of decimal digits. Space: O(1) besides conversion strings.
//
// @lc code=start

import (
	"strconv"
	"strings"
)

func CountDigitOccurrences3895(nums []int, digit int) int {
	target := strconv.Itoa(digit)
	total := 0
	for _, number := range nums {
		total += strings.Count(strconv.Itoa(number), target)
	}
	return total
}

// @lc code=end
