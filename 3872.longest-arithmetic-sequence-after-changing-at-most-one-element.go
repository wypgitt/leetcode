package leetcode

//
// @lc app=leetcode id=3872 lang=golang
//
// [3872] Longest Arithmetic Sequence After Changing At Most One Element
//
// Notes
// Work on adjacent differences. Precompute same-difference run lengths ending
// and starting at every diff index. Without a change, a run of d differences
// yields d+1 numbers; with one changed middle value, bridge nums[i-1] and
// nums[i+1] when their gap is even, then join compatible diff runs on both
// sides. Time: O(n). Space: O(n).
//
// @lc code=start

func LongestArithmetic3872(nums []int) int {
	n := len(nums)
	if n <= 2 {
		return n
	}

	diff := make([]int, n-1)
	for i := 0; i < n-1; i++ {
		diff[i] = nums[i+1] - nums[i]
	}
	diffCount := len(diff)

	left := make([]int, diffCount)
	for i := range left {
		left[i] = 1
	}
	for i := 1; i < diffCount; i++ {
		if diff[i] == diff[i-1] {
			left[i] = left[i-1] + 1
		}
	}

	right := make([]int, diffCount)
	for i := range right {
		right[i] = 1
	}
	for i := diffCount - 2; i >= 0; i-- {
		if diff[i] == diff[i+1] {
			right[i] = right[i+1] + 1
		}
	}

	longestDiffRun := 1
	for _, value := range left {
		if value > longestDiffRun {
			longestDiffRun = value
		}
	}
	answer := longestDiffRun + 2
	if answer > n {
		answer = n
	}

	for middle := 1; middle < n-1; middle++ {
		gap := nums[middle+1] - nums[middle-1]
		if gap%2 != 0 {
			continue
		}
		commonDifference := gap / 2

		leftCount := 0
		leftDiffIndex := middle - 2
		if leftDiffIndex >= 0 && diff[leftDiffIndex] == commonDifference {
			leftCount = left[leftDiffIndex]
		}
		rightCount := 0
		rightDiffIndex := middle + 1
		if rightDiffIndex < diffCount && diff[rightDiffIndex] == commonDifference {
			rightCount = right[rightDiffIndex]
		}
		if candidate := leftCount + 3 + rightCount; candidate > answer {
			answer = candidate
		}
	}

	return answer
}

// @lc code=end
