package leetcode

//
// @lc app=leetcode id=3830 lang=golang
//
// [3830] Longest Alternating Subarray After Removing At Most One Element
//
// Notes
// Store the comparison sign between adjacent values. Precompute alternating-run
// lengths ending at each index and starting at each index. Then try deleting one
// middle element and bridge nums[i-1] to nums[i+1], combining compatible left
// and right runs. Time: O(n). Space: O(n).
//
// @lc code=start

func LongestAlternating3830(nums []int) int {
	n := len(nums)
	if n <= 1 {
		return n
	}

	sign := make([]int, n-1)
	for i := 0; i < n-1; i++ {
		sign[i] = cmp3830(nums[i], nums[i+1])
	}

	endLen := make([]int, n)
	for i := range endLen {
		endLen[i] = 1
	}
	for i := 1; i < n; i++ {
		if sign[i-1] == 0 {
			endLen[i] = 1
		} else if i >= 2 && sign[i-2] == -sign[i-1] {
			endLen[i] = endLen[i-1] + 1
		} else {
			endLen[i] = 2
		}
	}

	startLen := make([]int, n)
	for i := range startLen {
		startLen[i] = 1
	}
	for i := n - 2; i >= 0; i-- {
		if sign[i] == 0 {
			startLen[i] = 1
		} else if i+2 < n && sign[i] == -sign[i+1] {
			startLen[i] = startLen[i+1] + 1
		} else {
			startLen[i] = 2
		}
	}

	answer := 1
	for _, length := range endLen {
		if length > answer {
			answer = length
		}
	}

	for removed := 1; removed < n-1; removed++ {
		bridge := cmp3830(nums[removed-1], nums[removed+1])
		if bridge == 0 {
			continue
		}

		left := 1
		if removed >= 2 && sign[removed-2] == -bridge {
			left = endLen[removed-1]
		}
		right := 1
		if removed+1 <= n-2 && sign[removed+1] == -bridge {
			right = startLen[removed+1]
		}
		if left+right > answer {
			answer = left + right
		}
	}

	return answer
}

func cmp3830(a, b int) int {
	if a < b {
		return 1
	}
	if a > b {
		return -1
	}
	return 0
}

// @lc code=end
