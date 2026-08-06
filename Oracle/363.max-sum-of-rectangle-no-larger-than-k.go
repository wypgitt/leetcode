package leetcode

//
// @lc app=leetcode id=363 lang=golang
//
// [363] Max Sum of Rectangle No Larger Than K
//
// Notes
// Fix two boundaries in the smaller matrix dimension and compress the other
// dimension into a 1-D array. The 1-D helper uses prefix sums and an ordered set
// query: for current prefix p, choose the smallest previous prefix >= p-k.
// Go has no built-in TreeSet, so this translation uses coordinate compression
// plus a Fenwick tree with order-statistic search. Time:
// O(min(R,C)^2 * max(R,C) log max(R,C)). Space: O(max(R,C)).
//
// @lc code=start

import "sort"

type fenwick363 struct {
	tree []int
}

func newFenwick363(size int) *fenwick363 {
	return &fenwick363{tree: make([]int, size+1)}
}

func (f *fenwick363) add(index, delta int) {
	for index < len(f.tree) {
		f.tree[index] += delta
		index += index & -index
	}
}

func (f *fenwick363) prefixSum(index int) int {
	total := 0
	for index > 0 {
		total += f.tree[index]
		index -= index & -index
	}
	return total
}

func (f *fenwick363) findByOrder(order int) int {
	index := 0
	bit := 1
	for bit<<1 < len(f.tree) {
		bit <<= 1
	}
	for bit > 0 {
		next := index + bit
		if next < len(f.tree) && f.tree[next] < order {
			index = next
			order -= f.tree[next]
		}
		bit >>= 1
	}
	return index + 1
}

func MaxSumSubmatrix363(matrix [][]int, k int) int {
	rows, cols := len(matrix), len(matrix[0])
	answer := negInf363

	bestSubarray := func(values []int) int {
		prefix := 0
		prefixes := make([]int, 0, len(values)+1)
		prefixes = append(prefixes, 0)
		for _, value := range values {
			prefix += value
			prefixes = append(prefixes, prefix)
		}

		sort.Ints(prefixes)
		unique := prefixes[:0]
		for _, value := range prefixes {
			if len(unique) == 0 || unique[len(unique)-1] != value {
				unique = append(unique, value)
			}
		}

		fenwick := newFenwick363(len(unique))
		best := negInf363
		prefix = 0
		fenwick.add(sort.SearchInts(unique, 0)+1, 1)

		for _, value := range values {
			prefix += value
			lowerIndex := sort.SearchInts(unique, prefix-k)
			seenBefore := fenwick.prefixSum(lowerIndex)
			totalSeen := fenwick.prefixSum(len(unique))
			if totalSeen > seenBefore {
				rank := fenwick.findByOrder(seenBefore + 1)
				previousPrefix := unique[rank-1]
				if prefix-previousPrefix > best {
					best = prefix - previousPrefix
				}
			}
			fenwick.add(sort.SearchInts(unique, prefix)+1, 1)
		}

		return best
	}

	if rows <= cols {
		for top := 0; top < rows; top++ {
			columnSums := make([]int, cols)
			for bottom := top; bottom < rows; bottom++ {
				for col := 0; col < cols; col++ {
					columnSums[col] += matrix[bottom][col]
				}
				if best := bestSubarray(columnSums); best > answer {
					answer = best
				}
				if answer == k {
					return k
				}
			}
		}
	} else {
		for left := 0; left < cols; left++ {
			rowSums := make([]int, rows)
			for right := left; right < cols; right++ {
				for row := 0; row < rows; row++ {
					rowSums[row] += matrix[row][right]
				}
				if best := bestSubarray(rowSums); best > answer {
					answer = best
				}
				if answer == k {
					return k
				}
			}
		}
	}

	return answer
}

const negInf363 = -1 << 60

// @lc code=end
