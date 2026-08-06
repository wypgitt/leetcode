/*
 * @lc app=leetcode id=3919 lang=java
 *
 * [3919] Minimum Cost to Move Between Indices
 *
 * Moving right across gap i costs 1 if i+1 is closest to i, otherwise the gap.
 * Moving left across the same gap costs 1 if i is closest to i+1. Prefix sums
 * of both directional costs answer queries in O(1).
 *
 * Time: O(n + q). Space: O(n).
 */

// @lc code=start
class Solution {
    public long[] minCost(int[] nums, int[][] queries) {
        int n = nums.length;
        long[] rightPrefix = new long[n];
        long[] leftPrefix = new long[n];

        for (int i = 0; i < n - 1; i++) {
            int gap = nums[i + 1] - nums[i];
            long rightStep = closest(nums, i) == i + 1 ? 1 : gap;
            long leftStep = closest(nums, i + 1) == i ? 1 : gap;
            rightPrefix[i + 1] = rightPrefix[i] + rightStep;
            leftPrefix[i + 1] = leftPrefix[i] + leftStep;
        }

        long[] answer = new long[queries.length];
        for (int q = 0; q < queries.length; q++) {
            int left = queries[q][0];
            int right = queries[q][1];
            if (left < right) {
                answer[q] = rightPrefix[right] - rightPrefix[left];
            } else {
                answer[q] = leftPrefix[left] - leftPrefix[right];
            }
        }
        return answer;
    }

    private int closest(int[] nums, int index) {
        int n = nums.length;
        if (index == 0) {
            return 1;
        }
        if (index == n - 1) {
            return n - 2;
        }
        int leftGap = nums[index] - nums[index - 1];
        int rightGap = nums[index + 1] - nums[index];
        return leftGap <= rightGap ? index - 1 : index + 1;
    }
}
// @lc code=end
