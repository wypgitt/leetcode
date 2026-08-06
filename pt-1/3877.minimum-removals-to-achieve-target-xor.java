/*
 * @lc app=leetcode id=3877 lang=java
 *
 * [3877] Minimum Removals to Achieve Target XOR
 *
 * Maximize how many elements we keep while obtaining each possible XOR.
 * dp[x] is the largest kept count producing XOR x. The answer removes all
 * other elements, or -1 if target is unreachable.
 *
 * Time: O(n * 2^14). Space: O(2^14).
 */

import java.util.Arrays;

// @lc code=start
class Solution {
    public int minRemovals(int[] nums, int target) {
        int maxXor = 1 << 14;
        int unreachable = -1_000_000_000;
        int[] dp = new int[maxXor];
        Arrays.fill(dp, unreachable);
        dp[0] = 0;

        for (int value : nums) {
            int[] next = dp.clone();
            for (int xor = 0; xor < maxXor; xor++) {
                if (dp[xor] == unreachable) {
                    continue;
                }
                int nx = xor ^ value;
                next[nx] = Math.max(next[nx], dp[xor] + 1);
            }
            dp = next;
        }

        return dp[target] == unreachable ? -1 : nums.length - dp[target];
    }
}
// @lc code=end
