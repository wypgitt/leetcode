/*
 * @lc app=leetcode id=2659 lang=java
 *
 * [2659] Make Array Empty
 */

// @lc code=start
import java.util.Arrays;

class Solution {
    public long countOperationsToEmptyArray(int[] nums) {
        int n = nums.length;
        Integer[] idx = new Integer[n];
        for (int i = 0; i < n; i++) {
            idx[i] = i;
        }
        Arrays.sort(idx, (i, j) -> Integer.compare(nums[i], nums[j]));
        long ans = n;
        for (int k = 1; k < n; k++) {
            if (idx[k] < idx[k - 1]) {
                ans += (long) (n - k);
            }
        }
        return ans;
    }
}
// @lc code=end
