/**
 * Algorithm:
 * Track both max and min product ending at the current position because a
 * negative number swaps their roles. The answer is the best max seen.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int maxProduct(int[] nums) {
        int curMax = nums[0];
        int curMin = nums[0];
        int ans = nums[0];
        for (int i = 1; i < nums.length; i++) {
            int num = nums[i];
            if (num < 0) {
                int tmp = curMax;
                curMax = curMin;
                curMin = tmp;
            }
            curMax = Math.max(num, curMax * num);
            curMin = Math.min(num, curMin * num);
            ans = Math.max(ans, curMax);
        }
        return ans;
    }
}

