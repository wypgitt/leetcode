/*
 * @lc app=leetcode id=2681 lang=java
 *
 * [2681] Power of Heroes
 */

// @lc code=start
import java.util.Arrays;

class Solution {
    private static final int MOD = 1_000_000_007;

    public int sumOfPower(int[] nums) {
        Arrays.sort(nums);
        long ans = 0;
        long p = 0;
        for (int x : nums) {
            long xx = (long) x * x % MOD;
            ans = (ans + xx * x % MOD + xx * p % MOD) % MOD;
            p = (p * 2 + x) % MOD;
        }
        return (int) ans;
    }
}
// @lc code=end
