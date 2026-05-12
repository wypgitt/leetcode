/*
 * 1043. Partition Array for Maximum Sum
 */
class Solution {
    public int maxSumAfterPartitioning(int[] arr, int k) {
        int[] dp = new int[arr.length + 1];

        for (int end = 1; end <= arr.length; end++) {
            int currentMax = 0;
            for (int length = 1; length <= k && length <= end; length++) {
                currentMax = Math.max(currentMax, arr[end - length]);
                dp[end] = Math.max(dp[end], dp[end - length] + currentMax * length);
            }
        }

        return dp[arr.length];
    }
}

/*
Interview Explanation

Core idea:
Look at the last partition. If it has length L, its contribution is L times
the maximum value in that block, plus the best answer for the prefix before it.

Java data structures:
- int[] dp where dp[end] is the best score for arr[0..end-1].
- currentMax maintains the maximum inside the candidate last block while we
  expand it backward.

Algorithm:
1. For every end position, try last block lengths 1 through k.
2. Update currentMax as the block grows leftward.
3. Candidate score is dp[end - length] + currentMax * length.
4. Store the best candidate in dp[end].

Correctness:
Every valid partition of a prefix has some final block length L <= k. The best
score before that block is dp[end - L], and the final block score is its
maximum times L. Trying every L considers every possible last partition, so the
DP returns the optimal total.

Complexity:
Time is O(nk), and space is O(n).

Edge cases:
- k = 1 returns the original sum.
- k = n allows the whole array as one block.
- Single-element array returns that element.
*/
