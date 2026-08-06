/*
 * @lc app=leetcode id=2702 lang=java
 *
 * [2702] Minimum Operations to Make Numbers Non-positive
 */

// @lc code=start
class Solution {
    public int minOperations(int[] nums, int x, int y) {
        int diff = x - y;
        int lo = 0;
        int hi = 0;
        for (int v : nums) {
            hi = Math.max(hi, v);
        }
        while (lo < hi) {
            int mid = (lo + hi) >>> 1;
            if (check(nums, diff, y, mid)) {
                hi = mid;
            } else {
                lo = mid + 1;
            }
        }
        return lo;
    }

    private boolean check(int[] nums, int diff, int y, int t) {
        long cnt = 0;
        long ty = (long) t * y;
        for (int v : nums) {
            if (v > ty) {
                cnt += (v - ty + diff - 1L) / diff;
                if (cnt > t) {
                    return false;
                }
            }
        }
        return cnt <= t;
    }
}
// @lc code=end
