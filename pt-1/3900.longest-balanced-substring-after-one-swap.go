package leetcode

//
// @lc app=leetcode id=3900 lang=golang
//
// [3900] Longest Balanced Substring After One Swap
//
// Notes
// Prefix balance (+1 for '1', -1 for '0') gives the longest already-balanced
// substring by equal prefix balances. One swap can fix substrings whose balance
// differs by 2, subject to having an opposite character outside; prefix-position
// lists plus binary search find the earliest allowed start under the length cap.
// Time: O(n log n). Space: O(n).
//
// @lc code=start

import "sort"

func LongestBalanced3900(s string) int {
	totalZeros := 0
	for i := range s {
		if s[i] == '0' {
			totalZeros++
		}
	}
	totalOnes := len(s) - totalZeros

	prefix := []int{0}
	positions := map[int][]int{0: {0}}
	balance := 0
	for index := 1; index <= len(s); index++ {
		if s[index-1] == '1' {
			balance++
		} else {
			balance--
		}
		prefix = append(prefix, balance)
		positions[balance] = append(positions[balance], index)
	}

	answer := 0
	earliest := map[int]int{}
	for index, bal := range prefix {
		if first, ok := earliest[bal]; ok {
			if index-first > answer {
				answer = index - first
			}
		} else {
			earliest[bal] = index
		}
	}

	capTooManyOnes := 2 * totalZeros
	capTooManyZeros := 2 * totalOnes
	for right, bal := range prefix {
		if right == 0 {
			continue
		}
		if best := bestWithCap3900(positions[bal-2], right, capTooManyOnes); best > answer {
			answer = best
		}
		if best := bestWithCap3900(positions[bal+2], right, capTooManyZeros); best > answer {
			answer = best
		}
	}

	return answer
}

func bestWithCap3900(starts []int, right int, cap int) int {
	if cap <= 0 {
		return 0
	}
	index := sort.SearchInts(starts, right-cap)
	if index < len(starts) && starts[index] < right {
		return right - starts[index]
	}
	return 0
}

// @lc code=end
