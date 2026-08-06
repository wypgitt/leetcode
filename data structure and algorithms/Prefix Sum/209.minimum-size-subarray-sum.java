/**
 * Algorithm:
 * Sliding window over positive numbers. Expand right to increase the sum; while
 * the sum is at least target, update the answer and shrink left.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int minSubArrayLen(int target, int[] nums) {
        int left = 0;
        int total = 0;
        int best = nums.length + 1;
        for (int right = 0; right < nums.length; right++) {
            total += nums[right];
            while (total >= target) {
                best = Math.min(best, right - left + 1);
                total -= nums[left++];
            }
        }
        return best == nums.length + 1 ? 0 : best;
    }
}

