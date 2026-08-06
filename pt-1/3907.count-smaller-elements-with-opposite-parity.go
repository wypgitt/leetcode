package leetcode

//
// @lc app=leetcode id=3907 lang=golang
//
// [3907] Count Smaller Elements With Opposite Parity
//
// Notes
// Scan from right to left. Two Fenwick trees store counts of seen even and odd
// values by compressed rank. For nums[i], query the opposite-parity tree for
// ranks smaller than its own, then insert nums[i] into its parity tree. Time:
// O(n log n). Space: O(n).
//
// @lc code=start

import "sort"

type fenwick3907 struct {
	tree []int
}

func newFenwick3907(size int) *fenwick3907 {
	return &fenwick3907{tree: make([]int, size+1)}
}

func (f *fenwick3907) add(index int, delta int) {
	for index < len(f.tree) {
		f.tree[index] += delta
		index += index & -index
	}
}

func (f *fenwick3907) query(index int) int {
	total := 0
	for index > 0 {
		total += f.tree[index]
		index -= index & -index
	}
	return total
}

func CountSmallerOppositeParity3907(nums []int) []int {
	values := append([]int(nil), nums...)
	sort.Ints(values)
	unique := values[:0]
	for _, value := range values {
		if len(unique) == 0 || unique[len(unique)-1] != value {
			unique = append(unique, value)
		}
	}

	evenTree := newFenwick3907(len(unique))
	oddTree := newFenwick3907(len(unique))
	answer := make([]int, len(nums))

	for i := len(nums) - 1; i >= 0; i-- {
		value := nums[i]
		pos := sort.SearchInts(unique, value) + 1
		if value%2 == 0 {
			answer[i] = oddTree.query(pos - 1)
			evenTree.add(pos, 1)
		} else {
			answer[i] = evenTree.query(pos - 1)
			oddTree.add(pos, 1)
		}
	}

	return answer
}

// @lc code=end
