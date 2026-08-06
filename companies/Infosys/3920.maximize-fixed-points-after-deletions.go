package leetcode

//
// @lc app=leetcode id=3920 lang=golang
//
// [3920] Maximize Fixed Points After Deletions
//
// Notes
// If nums[i] becomes fixed after deletions, the number of deleted elements
// before i must equal i-nums[i], so group candidates by value and use a Fenwick
// tree storing maximum chain length by deleted-before count. Process values in
// increasing order and batch updates within the same value to avoid reusing it.
// Time: O(n log n). Space: O(n).
//
// @lc code=start

import "sort"

type fenwickMax3920 struct {
	tree []int
}

func newFenwickMax3920(size int) *fenwickMax3920 {
	return &fenwickMax3920{tree: make([]int, size+1)}
}

func (f *fenwickMax3920) update(index int, value int) {
	index++
	for index < len(f.tree) {
		if value > f.tree[index] {
			f.tree[index] = value
		}
		index += index & -index
	}
}

func (f *fenwickMax3920) query(index int) int {
	index++
	best := 0
	for index > 0 {
		if f.tree[index] > best {
			best = f.tree[index]
		}
		index -= index & -index
	}
	return best
}

func MaxFixedPoints3920(nums []int) int {
	n := len(nums)
	groups := map[int][]int{}
	for i, value := range nums {
		if value <= i {
			groups[value] = append(groups[value], i-value)
		}
	}

	keys := make([]int, 0, len(groups))
	for value := range groups {
		keys = append(keys, value)
	}
	sort.Ints(keys)

	bit := newFenwickMax3920(n)
	answer := 0
	for _, value := range keys {
		pending := [][2]int{}
		for _, deletedBefore := range groups[value] {
			best := bit.query(deletedBefore) + 1
			pending = append(pending, [2]int{deletedBefore, best})
			if best > answer {
				answer = best
			}
		}
		for _, item := range pending {
			bit.update(item[0], item[1])
		}
	}
	return answer
}

// @lc code=end
