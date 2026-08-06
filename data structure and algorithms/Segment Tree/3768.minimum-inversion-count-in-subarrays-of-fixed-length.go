package leetcode

//
// @lc app=leetcode id=3768 lang=golang
//
// [3768] Minimum Inversion Count in Subarrays of Fixed Length
//
// Notes
// Coordinate-compress nums and maintain the current window in a Fenwick tree.
// Build the first window by counting previous elements greater than each insert.
// When sliding, removing nums[left] deletes exactly the inversions where it was
// the left/larger element, equal to the number of smaller values still inside;
// inserting nums[right] adds the number of greater values already inside.
// Time: O(n log n). Space: O(n).
//
// @lc code=start

import "sort"

type fenwick3768 struct {
	tree []int
}

func newFenwick3768(size int) *fenwick3768 {
	return &fenwick3768{tree: make([]int, size+1)}
}

func (f *fenwick3768) add(index, delta int) {
	for index < len(f.tree) {
		f.tree[index] += delta
		index += index & -index
	}
}

func (f *fenwick3768) prefixSum(index int) int {
	total := 0
	for index > 0 {
		total += f.tree[index]
		index -= index & -index
	}
	return total
}

func MinInversionCount3768(nums []int, k int) int {
	if k <= 1 {
		return 0
	}

	values := append([]int(nil), nums...)
	sort.Ints(values)
	unique := values[:0]
	for _, value := range values {
		if len(unique) == 0 || unique[len(unique)-1] != value {
			unique = append(unique, value)
		}
	}

	ranks := make([]int, len(nums))
	for i, value := range nums {
		ranks[i] = sort.SearchInts(unique, value) + 1
	}

	fenwick := newFenwick3768(len(unique))
	currentInversions := 0
	for index := 0; index < k; index++ {
		rank := ranks[index]
		greaterCount := index - fenwick.prefixSum(rank)
		currentInversions += greaterCount
		fenwick.add(rank, 1)
	}

	answer := currentInversions
	for right := k; right < len(nums); right++ {
		left := right - k

		outgoingRank := ranks[left]
		smallerCount := fenwick.prefixSum(outgoingRank - 1)
		currentInversions -= smallerCount
		fenwick.add(outgoingRank, -1)

		incomingRank := ranks[right]
		greaterCount := (k - 1) - fenwick.prefixSum(incomingRank)
		currentInversions += greaterCount
		fenwick.add(incomingRank, 1)

		if currentInversions < answer {
			answer = currentInversions
		}
	}

	return answer
}

// @lc code=end
