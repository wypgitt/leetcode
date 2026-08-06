/**
 * Algorithm:
 * Kadane's algorithm tracks the best subarray ending at the current index.
 * Either extend the previous subarray or start fresh at the current number.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int maxSubArray(int[] nums) {
        int current = nums[0];
        int best = nums[0];
        for (int i = 1; i < nums.length; i++) {
            current = Math.max(nums[i], current + nums[i]);
            best = Math.max(best, current);
        }
        return best;
    }
}

