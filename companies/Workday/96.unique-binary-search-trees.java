/**
 * Algorithm:
 * Catalan DP. Choosing a root splits the remaining nodes into independent left
 * and right subtree sizes, contributing dp[left] * dp[right].
 *
 * Complexity:
 * Time O(n^2), space O(n).
 */
class Solution {
    public int numTrees(int n) {
        int[] dp = new int[n + 1];
        dp[0] = 1;
        dp[1] = 1;
        for (int nodes = 2; nodes <= n; nodes++) {
            int total = 0;
            for (int leftCount = 0; leftCount < nodes; leftCount++) {
                total += dp[leftCount] * dp[nodes - 1 - leftCount];
            }
            dp[nodes] = total;
        }
        return dp[n];
    }
}

