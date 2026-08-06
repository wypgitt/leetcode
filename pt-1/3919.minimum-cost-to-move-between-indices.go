package leetcode

//
// @lc app=leetcode id=3919 lang=golang
//
// [3919] Minimum Cost to Move Between Indices
//
// Notes
// Precompute directional prefix costs between adjacent indices. Moving right
// from i to i+1 costs 1 if i+1 is the closest neighbor of i, otherwise the value
// gap; moving left uses the symmetric closest check for i+1. Each query becomes
// a prefix-difference lookup. Time: O(n+q). Space: O(n).
//
// @lc code=start

func MinCost3919(nums []int, queries [][]int) []int {
	n := len(nums)
	rightPrefix := make([]int, n)
	leftPrefix := make([]int, n)

	for i := 0; i < n-1; i++ {
		gap := nums[i+1] - nums[i]

		rightStep := gap
		if closest3919(nums, i) == i+1 {
			rightStep = 1
		}
		leftStep := gap
		if closest3919(nums, i+1) == i {
			leftStep = 1
		}

		rightPrefix[i+1] = rightPrefix[i] + rightStep
		leftPrefix[i+1] = leftPrefix[i] + leftStep
	}

	answer := make([]int, len(queries))
	for i, query := range queries {
		left, right := query[0], query[1]
		if left < right {
			answer[i] = rightPrefix[right] - rightPrefix[left]
		} else {
			answer[i] = leftPrefix[left] - leftPrefix[right]
		}
	}
	return answer
}

func closest3919(nums []int, index int) int {
	n := len(nums)
	if index == 0 {
		return 1
	}
	if index == n-1 {
		return n - 2
	}
	leftGap := nums[index] - nums[index-1]
	rightGap := nums[index+1] - nums[index]
	if leftGap <= rightGap {
		return index - 1
	}
	return index + 1
}

// @lc code=end
