/**
 * Algorithm:
 * Dynamic programming with two rolling values. prev1 is the best up to the
 * previous house; prev2 is the best before that. For each house, choose skip or
 * rob.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int rob(int[] nums) {
        int prev2 = 0;
        int prev1 = 0;
        for (int num : nums) {
            int cur = Math.max(prev1, prev2 + num);
            prev2 = prev1;
            prev1 = cur;
        }
        return prev1;
    }
}

