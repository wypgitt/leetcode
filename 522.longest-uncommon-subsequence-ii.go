package leetcode

//
// @lc app=leetcode id=522 lang=golang
//
// [522] Longest Uncommon Subsequence II
//
// Notes
// Test candidate strings from longest to shortest. A string is uncommon if it
// is not a subsequence of any other string with length at least as large. The
// first uncommon candidate in descending length order is optimal. Time:
// O(n^2 * L). Space: O(n) for the order slice.
//
// @lc code=start

import "sort"

func FindLUSlength522(strs []string) int {
	order := make([]int, len(strs))
	for i := range order {
		order[i] = i
	}
	sort.Slice(order, func(i, j int) bool {
		return len(strs[order[i]]) > len(strs[order[j]])
	})

	for _, index := range order {
		candidate := strs[index]
		uncommon := true
		for otherIndex, other := range strs {
			if otherIndex == index {
				continue
			}
			if len(other) >= len(candidate) && isSubsequence522(candidate, other) {
				uncommon = false
				break
			}
		}
		if uncommon {
			return len(candidate)
		}
	}
	return -1
}

func isSubsequence522(small string, large string) bool {
	pointer := 0
	for i := range large {
		if pointer < len(small) && small[pointer] == large[i] {
			pointer++
		}
	}
	return pointer == len(small)
}

// @lc code=end
