package leetcode

//
// @lc app=leetcode id=3806 lang=golang
//
// [3806] Maximum Bitwise AND After Increment Operations
//
// Notes
// Greedily test answer bits from high to low. For a candidate mask, compute the
// minimum increment needed for each number to become a supermask of it, sort
// those costs, and check whether the cheapest m numbers fit in budget k. The
// bitwise cost routine jumps upward at the highest missing required bit.
// Time: O(B * n log n). Space: O(n).
//
// @lc code=start

import "sort"

const maxBit3806 = 31

func MaximumAND3806(nums []int, k int, m int) int {
	answer := 0
	for bit := maxBit3806; bit >= 0; bit-- {
		candidate := answer | (1 << bit)
		if canMake3806(nums, k, m, candidate) {
			answer = candidate
		}
	}
	return answer
}

func canMake3806(nums []int, budget int, count int, mask int) bool {
	costs := make([]int, len(nums))
	for i, value := range nums {
		costs[i] = costToContain3806(value, mask)
	}
	sort.Ints(costs)
	total := 0
	for i := 0; i < count; i++ {
		total += costs[i]
		if total > budget {
			return false
		}
	}
	return total <= budget
}

func costToContain3806(value int, mask int) int {
	target := value
	for bit := maxBit3806; bit >= 0; bit-- {
		if ((mask>>bit)&1) == 1 && ((target>>bit)&1) == 0 {
			target = ((target >> bit) + 1) << bit
			target |= mask & ((1 << bit) - 1)
		}
	}
	return target - value
}

// @lc code=end
