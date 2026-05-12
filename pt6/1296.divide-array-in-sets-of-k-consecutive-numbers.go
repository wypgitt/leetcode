package main

import "sort"

func isPossibleDivide(nums []int, k int) bool {
	if len(nums)%k != 0 {
		return false
	}

	count := map[int]int{}
	for _, num := range nums {
		count[num]++
	}
	sort.Ints(nums)

	for _, start := range nums {
		amount := count[start]
		if amount == 0 {
			continue
		}
		for value := start; value < start+k; value++ {
			if count[value] < amount {
				return false
			}
			count[value] -= amount
		}
	}

	return true
}

/*
Explanation

Process numbers in sorted order. If count[start] is positive, those copies
must start groups at start because no smaller number remains available to use
them. Therefore each value start through start+k-1 must have at least that many
copies, and we subtract them.

The count map stores multiplicities, and sorting gives the greedy order that
makes each group start forced.

Edge cases: length not divisible by k; missing middle value; many duplicates.

Time complexity: O(n log n + g*k), where g is the number of distinct group
starts processed.
Space complexity: O(n).
*/
