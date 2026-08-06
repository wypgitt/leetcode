/*
 * @lc app=leetcode id=3909 lang=java
 *
 * [3909] Compare Sums of Bitonic Parts
 *
 * Find the peak index, sum the ascending part through the peak and the
 * descending part from the peak. Return 0 if the ascending sum is larger, 1 if
 * descending is larger, otherwise -1.
 *
 * Time: O(n). Space: O(1).
 */

// @lc code=start
class Solution {
    public int compareBitonicSums(int[] nums) {
        int peak = 0;
        for (int i = 1; i < nums.length; i++) {
            if (nums[i] > nums[peak]) {
                peak = i;
            }
        }

        long ascending = 0;
        for (int i = 0; i <= peak; i++) {
            ascending += nums[i];
        }
        long descending = 0;
        for (int i = peak; i < nums.length; i++) {
            descending += nums[i];
        }

        if (ascending > descending) {
            return 0;
        }
        if (descending > ascending) {
            return 1;
        }
        return -1;
    }
}
// @lc code=end
