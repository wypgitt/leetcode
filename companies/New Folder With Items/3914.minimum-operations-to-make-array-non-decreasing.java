/*
 * @lc app=leetcode id=3914 lang=java
 *
 * [3914] Minimum Operations to Make Array Non Decreasing
 *
 * Smallest non-decreasing majorant v; cost = sum of positive jumps in d[i]=v[i]-nums[i].
 */

// @lc code=start
class Solution {
    public long minOperations(int[] nums) {
        int n = nums.length;
        if (n == 1) {
            return 0;
        }
        long curV = nums[0];
        long prevD = curV - nums[0];
        long ans = Math.max(0, prevD);

        for (int i = 1; i < n; i++) {
            curV = Math.max(nums[i], curV);
            long curD = curV - nums[i];
            ans += Math.max(0, curD - prevD);
            prevD = curD;
        }
        return ans;
    }
}
// @lc code=end
