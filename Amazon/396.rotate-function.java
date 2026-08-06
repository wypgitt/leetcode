/**
 * Algorithm:
 * Compute F(0), then update rotations with
 * F(k) = F(k - 1) + sum(nums) - n * nums[n - k]. Rotating right increases
 * every old index by one, then the moved last element loses n positions.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int maxRotateFunction(int[] nums) {
        int n = nums.length;
        int total = 0;
        int cur = 0;
        for (int i = 0; i < n; i++) {
            total += nums[i];
            cur += i * nums[i];
        }
        int best = cur;
        for (int k = 1; k < n; k++) {
            cur = cur + total - n * nums[n - k];
            best = Math.max(best, cur);
        }
        return best;
    }
}

