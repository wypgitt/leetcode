/*
 * @lc app=leetcode id=2585 lang=java
 *
 * [2585] Number of Ways to Earn Points
 */

/*
 * Bounded knapsack counting: {@code dp[j]} = ways to score exactly {@code j} using
 * types processed so far. For each type {@code (cnt, w)}, {@code cur[j] = sum_k
 * prev[j - k*w]} for k in 0..min(cnt, j/w).
 *
 * Time: O(types · target · avg copies per layer). Space: O(target).
 * =============================================================================
 */

// @lc code=start
class Solution {
    private static final int MOD = 1_000_000_007;

    public int waysToReachTarget(int target, int[][] types) {
        int[] prev = new int[target + 1];
        prev[0] = 1;
        for (int[] t : types) {
            int cnt = t[0];
            int w = t[1];
            int[] cur = new int[target + 1];
            for (int j = 0; j <= target; j++) {
                int upto = Math.min(cnt, j / w);
                int acc = 0;
                for (int k = 0; k <= upto; k++) {
                    acc = (acc + prev[j - k * w]) % MOD;
                }
                cur[j] = acc;
            }
            prev = cur;
        }
        return prev[target] % MOD;
    }
}
// @lc code=end
