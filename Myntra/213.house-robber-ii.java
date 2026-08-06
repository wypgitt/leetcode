/**
 * Algorithm:
 * Houses form a cycle, so the first and last cannot both be robbed. Solve two
 * linear robber subproblems: exclude last, and exclude first.
 *
 * Complexity:
 * Time O(n), space O(1).
 */
class Solution {
    public int rob(int[] nums) {
        if (nums.length == 1) {
            return nums[0];
        }
        return Math.max(robLine(nums, 0, nums.length - 2), robLine(nums, 1, nums.length - 1));
    }

    private int robLine(int[] nums, int lo, int hi) {
        int prev2 = 0;
        int prev1 = 0;
        for (int i = lo; i <= hi; i++) {
            int cur = Math.max(prev1, prev2 + nums[i]);
            prev2 = prev1;
            prev1 = cur;
        }
        return prev1;
    }
}

