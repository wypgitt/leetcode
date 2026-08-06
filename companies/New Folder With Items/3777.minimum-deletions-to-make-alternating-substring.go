package leetcode

//
// @lc app=leetcode id=3777 lang=golang
//
// [3777] Minimum Deletions to Make Alternating Substring
//
// Notes
// A substring with t transitions between adjacent characters has t+1 runs.
// Deleting all but one character from each run is optimal, so deletions =
// length - runs. Store the transition bit for each edge in a Fenwick tree so
// point flips update only the two neighboring edges and range queries are
// logarithmic. Time: O((n+q) log n). Space: O(n).
//
// @lc code=start

type fenwick3777 struct {
	tree []int
}

func newFenwick3777(size int) *fenwick3777 {
	if size < 1 {
		size = 1
	}
	return &fenwick3777{tree: make([]int, size+1)}
}

func (f *fenwick3777) add(index, delta int) {
	index++
	for index < len(f.tree) {
		f.tree[index] += delta
		index += index & -index
	}
}

func (f *fenwick3777) prefixSum(index int) int {
	total := 0
	index++
	for index > 0 {
		total += f.tree[index]
		index -= index & -index
	}
	return total
}

func (f *fenwick3777) rangeSum(left, right int) int {
	if left > right {
		return 0
	}
	total := f.prefixSum(right)
	if left > 0 {
		total -= f.prefixSum(left - 1)
	}
	return total
}

func MinDeletions3777(s string, queries [][]int) []int {
	chars := []byte(s)
	n := len(chars)
	fenwick := newFenwick3777(n - 1)

	edgeValue := func(index int) int {
		if chars[index] != chars[index+1] {
			return 1
		}
		return 0
	}

	for index := 0; index < n-1; index++ {
		if edgeValue(index) == 1 {
			fenwick.add(index, 1)
		}
	}

	refreshEdge := func(index, oldValue int) {
		if index < 0 || index >= n-1 {
			return
		}
		newValue := edgeValue(index)
		if newValue != oldValue {
			fenwick.add(index, newValue-oldValue)
		}
	}

	answer := []int{}
	for _, query := range queries {
		if query[0] == 1 {
			index := query[1]
			leftOld := 0
			if index > 0 {
				leftOld = edgeValue(index - 1)
			}
			rightOld := 0
			if index < n-1 {
				rightOld = edgeValue(index)
			}

			if chars[index] == 'A' {
				chars[index] = 'B'
			} else {
				chars[index] = 'A'
			}

			refreshEdge(index-1, leftOld)
			refreshEdge(index, rightOld)
		} else {
			left, right := query[1], query[2]
			transitions := fenwick.rangeSum(left, right-1)
			length := right - left + 1
			runs := transitions + 1
			answer = append(answer, length-runs)
		}
	}

	return answer
}

// @lc code=end
