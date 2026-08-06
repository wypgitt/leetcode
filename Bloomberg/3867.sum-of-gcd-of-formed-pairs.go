package leetcode

//
// @lc app=leetcode id=3867 lang=golang
//
// [3867] Sum of GCD of Formed Pairs
//
// Notes
// Maintain the running maximum and append gcd(current value, running maximum)
// for each prefix. Sorting those derived values and pairing smallest with
// largest matches the Python strategy, then sum gcds of each pair. Time:
// O(n log n). Space: O(n).
//
// @lc code=start

import "sort"

func GcdSum3867(nums []int) int {
	prefixGCD := make([]int, 0, len(nums))
	runningMax := 0
	for _, value := range nums {
		if value > runningMax {
			runningMax = value
		}
		prefixGCD = append(prefixGCD, gcd3867(value, runningMax))
	}

	sort.Ints(prefixGCD)
	answer := 0
	left, right := 0, len(prefixGCD)-1
	for left < right {
		answer += gcd3867(prefixGCD[left], prefixGCD[right])
		left++
		right--
	}
	return answer
}

func gcd3867(a, b int) int {
	for b != 0 {
		a, b = b, a%b
	}
	if a < 0 {
		return -a
	}
	return a
}

// @lc code=end
