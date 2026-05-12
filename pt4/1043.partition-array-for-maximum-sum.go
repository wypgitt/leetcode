package main

/*
1043. Partition Array for Maximum Sum
*/
func maxSumAfterPartitioning(arr []int, k int) int {
	dp := make([]int, len(arr)+1)

	for end := 1; end <= len(arr); end++ {
		currentMax := 0
		for length := 1; length <= k && length <= end; length++ {
			if arr[end-length] > currentMax {
				currentMax = arr[end-length]
			}
			candidate := dp[end-length] + currentMax*length
			if candidate > dp[end] {
				dp[end] = candidate
			}
		}
	}

	return dp[len(arr)]
}

/*
Interview Explanation

Core idea:
Look at the last partition. If its length is L, its contribution is L times
the maximum value in that block plus the best answer for the prefix before it.

Go data structures:
- []int dp where dp[end] is the best score for arr[:end].
- currentMax tracks the maximum of the candidate last block as it expands
  backward.

Algorithm:
1. For every end position, try each possible last-block length up to k.
2. Update currentMax while extending the block left.
3. Candidate score is dp[end-length] + currentMax*length.
4. Keep the best candidate.

Correctness:
Every valid partition of arr[:end] has a final block length L <= k. The prefix
before that block is optimally dp[end-L], and the block score is max(block)*L.
Trying every possible L considers every final partition, so the DP is optimal.

Complexity:
Time is O(n*k). Space is O(n).

Edge cases:
- k = 1 returns the original sum.
- k = len(arr) can choose the whole array as one block.
- Single element returns itself.
*/
