/*
 * @lc app=leetcode id=3865 lang=java
 *
 * [3865] Reverse K Subarrays
 *
 * The Python solution divides the array into k equal-length blocks
 * len(nums) / k and reverses each block into the output.
 *
 * Time: O(n). Space: O(n) for the returned array.
 */

// @lc code=start
class Solution {
    public int[] reverseSubarrays(int[] nums, int k) {
        int blockLength = nums.length / k;
        int[] result = new int[nums.length];
        int write = 0;

        for (int start = 0; start < nums.length; start += blockLength) {
            int end = Math.min(nums.length, start + blockLength);
            for (int i = end - 1; i >= start; i--) {
                result[write++] = nums[i];
            }
        }
        return result;
    }
}
// @lc code=end
