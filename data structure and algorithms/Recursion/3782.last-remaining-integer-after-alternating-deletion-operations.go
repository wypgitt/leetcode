package leetcode

//
// @lc app=leetcode id=3782 lang=golang
//
// [3782] Last Remaining Integer After Alternating Deletion Operations
//
// Notes
// The remaining numbers always form an arithmetic progression. Track its first
// value, step, count, and deletion direction. For this variant's survivor
// progression, only a right-side pass with an even count advances the tracked
// first value. Time:
// O(log n). Space: O(1).
//
// @lc code=start

func LastInteger3782(n int) int {
	first := 1
	step := 1
	count := n
	deleteFromLeft := true

	for count > 1 {
		if !deleteFromLeft && count%2 == 0 {
			first += step
		}
		count = (count + 1) / 2
		step *= 2
		deleteFromLeft = !deleteFromLeft
	}

	return first
}

// @lc code=end
