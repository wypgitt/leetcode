package main

func longestSubsequence(arr []int, difference int) int {
	bestEndingAt := map[int]int{}
	best := 0

	for _, num := range arr {
		bestEndingAt[num] = bestEndingAt[num-difference] + 1
		if bestEndingAt[num] > best {
			best = bestEndingAt[num]
		}
	}

	return best
}

/*
Explanation

Let dp[x] be the longest valid subsequence ending with value x after processing
the current prefix. When the next value is num, the previous value must be
num-difference, so dp[num] = dp[num-difference] + 1.

The map is the right data structure because values can be negative or large;
an array indexed by value would be wasteful. Scanning left to right preserves
subsequence order.

Edge cases: difference == 0 counts repeated equal values; negative difference
uses the same formula; missing predecessors default to zero in Go maps.

Time complexity: O(n) average.
Space complexity: O(u), where u is the number of distinct values.
*/
