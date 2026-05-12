package main

/*
1027. Longest Arithmetic Subsequence
*/
func longestArithSeqLength(nums []int) int {
	dp := make([]map[int]int, len(nums))
	for i := range dp {
		dp[i] = make(map[int]int)
	}

	best := 2
	for right := 0; right < len(nums); right++ {
		for left := 0; left < right; left++ {
			diff := nums[right] - nums[left]
			length := dp[left][diff] + 1
			if dp[left][diff] == 0 {
				length = 2
			}
			if length > dp[right][diff] {
				dp[right][diff] = length
			}
			if dp[right][diff] > best {
				best = dp[right][diff]
			}
		}
	}

	return best
}

/*
Interview Explanation

Core idea:
An arithmetic subsequence is determined by its last index and common
difference. If a sequence ending at left has difference d, nums[right] can
extend it when nums[right] - nums[left] == d.

Go data structures:
- []map[int]int stores a map for each ending index.
- The map key is the difference, and the value is the best length ending at
  that index with that difference. A map is natural because differences can be
  negative and sparse.

Algorithm:
For every pair left < right:
1. Compute diff.
2. Extend the best sequence ending at left with that diff, or start a length-2
   sequence if none exists.
3. Store the best length in dp[right][diff].
4. Track the global maximum.

Correctness:
Every arithmetic subsequence of length at least two has a final pair and a
common difference. The transition considers that final pair and extends the
best valid earlier sequence. Since all pairs are processed, every possible
subsequence ending is represented, and the maximum is the answer.

Complexity:
There are O(n^2) pairs and average O(1) map operations, so time is O(n^2).
Space is O(n^2) in the worst case.

Edge cases:
- Equal values use diff 0.
- Decreasing sequences use negative differences.
- Minimum input length 2 returns 2.
*/
