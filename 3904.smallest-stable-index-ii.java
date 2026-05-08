/*
 * @lc app=leetcode id=3904 lang=java
 *
 * [3904] Smallest Stable Index II
 *
 * Precompute suffix minimums. Scan left-to-right while maintaining prefix max;
 * the first index where prefixMax - suffixMin[i] <= k is stable.
 *
 * Time: O(n). Space: O(n).
 */

// @lc code=start
class Solution {
    public int firstStableIndex(int[] nums, int k) {
        int n = nums.length;
        int[] suffixMin = new int[n];
        suffixMin[n - 1] = nums[n - 1];
        for (int i = n - 2; i >= 0; i--) {
            suffixMin[i] = Math.min(nums[i], suffixMin[i + 1]);
        }

        int prefixMax = 0;
        for (int i = 0; i < n; i++) {
            prefixMax = Math.max(prefixMax, nums[i]);
            if (prefixMax - suffixMin[i] <= k) {
                return i;
            }
        }
        return -1;
    }
}
// @lc code=end
