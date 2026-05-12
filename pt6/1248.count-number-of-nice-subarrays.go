package main

func numberOfSubarrays(nums []int, k int) int {
	prefixFreq := map[int]int{0: 1}
	oddCount, total := 0, 0

	for _, num := range nums {
		oddCount += num % 2
		total += prefixFreq[oddCount-k]
		prefixFreq[oddCount]++
	}

	return total
}

/*
Explanation

Track the prefix count of odd numbers. A subarray ending at the current index
has exactly k odds when a previous prefix had oddCount-k odds. The map stores
how often each prefix odd count has appeared.

This is the same data-structure pattern as subarray sum equals k: a running
prefix value plus a frequency map.

Edge cases: even numbers create repeated prefix counts; fewer than k odds
returns 0; k == 1 works without special handling.

Time complexity: O(n).
Space complexity: O(n) in the worst case.
*/
