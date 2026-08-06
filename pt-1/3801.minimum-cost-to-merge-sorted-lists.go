package leetcode

//
// @lc app=leetcode id=3801 lang=golang
//
// [3801] Minimum Cost to Merge Sorted Lists
//
// Notes
// This is subset DP over lists. Precompute each subset's total length and
// median, then split every subset into two non-empty parts and pay child costs
// plus total length plus median distance. Sorted input lists allow median
// queries by binary searching over the global distinct values and precomputed
// per-list <= counts. Time: O(3^m + 2^m*m*log V). Space: O(2^m*m).
//
// @lc code=start

import "sort"

func MinMergeCost3801(lists [][]int) int {
	listCount := len(lists)
	maskCount := 1 << listCount

	lengths := make([]int, maskCount)
	medians := make([]int, maskCount)
	members := make([][]int, maskCount)
	for mask := 1; mask < maskCount; mask++ {
		lowestBit := mask & -mask
		listIndex := bitIndex3801(lowestBit)
		previousMask := mask ^ lowestBit
		lengths[mask] = lengths[previousMask] + len(lists[listIndex])
		members[mask] = append(append([]int(nil), members[previousMask]...), listIndex)
	}

	distinctValues := []int{}
	for _, values := range lists {
		distinctValues = append(distinctValues, values...)
	}
	sort.Ints(distinctValues)
	unique := distinctValues[:0]
	for _, value := range distinctValues {
		if len(unique) == 0 || unique[len(unique)-1] != value {
			unique = append(unique, value)
		}
	}
	distinctValues = unique

	countLeq := make([][]int, listCount)
	for i, values := range lists {
		countLeq[i] = make([]int, len(distinctValues))
		for j, candidate := range distinctValues {
			countLeq[i][j] = sort.Search(len(values), func(pos int) bool {
				return values[pos] > candidate
			})
		}
	}

	findSubsetMedian := func(mask int) int {
		target := (lengths[mask]-1)/2 + 1
		left, right := 0, len(distinctValues)-1
		for left < right {
			middle := (left + right) / 2
			count := 0
			for _, listIndex := range members[mask] {
				count += countLeq[listIndex][middle]
			}
			if count >= target {
				right = middle
			} else {
				left = middle + 1
			}
		}
		return distinctValues[left]
	}

	for mask := 1; mask < maskCount; mask++ {
		medians[mask] = findSubsetMedian(mask)
	}

	const inf = 1 << 60
	dp := make([]int, maskCount)
	for i := range dp {
		dp[i] = inf
	}
	for i := 0; i < listCount; i++ {
		dp[1<<i] = 0
	}

	for mask := 1; mask < maskCount; mask++ {
		if mask&(mask-1) == 0 {
			continue
		}
		best := inf
		totalLength := lengths[mask]
		for submask := (mask - 1) & mask; submask > 0; submask = (submask - 1) & mask {
			other := mask ^ submask
			if submask < other {
				candidate := dp[submask] + dp[other] + totalLength + abs3801(medians[submask]-medians[other])
				if candidate < best {
					best = candidate
				}
			}
		}
		dp[mask] = best
	}

	return dp[maskCount-1]
}

func bitIndex3801(bit int) int {
	index := 0
	for bit > 1 {
		bit >>= 1
		index++
	}
	return index
}

func abs3801(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

// @lc code=end
