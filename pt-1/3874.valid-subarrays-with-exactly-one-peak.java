/*
 * @lc app=leetcode id=3874 lang=java
 *
 * [3874] Valid Subarrays With Exactly One Peak
 *
 * Enumerate every peak. A valid subarray containing this peak cannot cross the
 * previous/next peak and must stay within distance k of the peak on both sides.
 * Multiply valid left endpoint choices by valid right endpoint choices.
 *
 * Time: O(n). Space: O(number of peaks).
 */

import java.util.ArrayList;
import java.util.List;

// @lc code=start
class Solution {
    public long validSubarrays(int[] nums, int k) {
        int n = nums.length;
        List<Integer> peaks = new ArrayList<>();
        for (int i = 1; i < n - 1; i++) {
            if (nums[i] > nums[i - 1] && nums[i] > nums[i + 1]) {
                peaks.add(i);
            }
        }

        long answer = 0;
        for (int i = 0; i < peaks.size(); i++) {
            int peak = peaks.get(i);
            int prevPeak = i > 0 ? peaks.get(i - 1) : -1;
            int nextPeak = i + 1 < peaks.size() ? peaks.get(i + 1) : n;

            int leftMin = Math.max(Math.max(0, peak - k), prevPeak + 1);
            int rightMax = Math.min(Math.min(n - 1, peak + k), nextPeak - 1);
            answer += (long) (peak - leftMin + 1) * (rightMax - peak + 1);
        }
        return answer;
    }
}
// @lc code=end
