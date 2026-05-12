package main

/*
1035. Uncrossed Lines
*/
func maxUncrossedLines(nums1 []int, nums2 []int) int {
	dp := make([]int, len(nums2)+1)

	for _, value1 := range nums1 {
		previousDiagonal := 0
		for j, value2 := range nums2 {
			oldDPJ := dp[j+1]
			if value1 == value2 {
				dp[j+1] = previousDiagonal + 1
			} else if dp[j] > dp[j+1] {
				dp[j+1] = dp[j]
			}
			previousDiagonal = oldDPJ
		}
	}

	return dp[len(nums2)]
}

/*
Interview Explanation

Core idea:
Uncrossed lines are exactly the Longest Common Subsequence problem. Once we
connect nums1[i] to nums2[j], future lines must use larger indices in both
arrays.

Go data structures:
- []int dp is a one-row compressed LCS table.
- previousDiagonal stores the previous row's dp[j-1] value, which is needed
  when the current values match.

Algorithm:
1. Iterate nums1 as the outer dimension.
2. For each value, scan nums2.
3. If values match, extend the old diagonal by one.
4. Otherwise, keep the better value from skipping one side.

Correctness:
For each pair of prefixes, the optimal LCS either matches the last values or
skips one last value. The update implements that recurrence. Since every
uncrossed line set is a common subsequence and every common subsequence can be
drawn uncrossed, the DP answer is the maximum number of lines.

Complexity:
Time is O(m*n). Space is O(n), where n is len(nums2).

Edge cases:
- No common values returns 0.
- Duplicate values are handled by subsequence ordering.
- One-element arrays work naturally.
*/
