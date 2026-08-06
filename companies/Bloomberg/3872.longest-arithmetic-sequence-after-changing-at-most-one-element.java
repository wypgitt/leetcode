/*
 * @lc app=leetcode id=3872 lang=java
 *
 * [3872] Longest Arithmetic Sequence After Changing at Most One Element
 *
 * Work on adjacent differences. left/right store equal-difference run lengths.
 * Without a change, a run of d differences gives run+1 elements; with one
 * changed middle element, bridge nums[i-1] and nums[i+1] if their gap is even.
 *
 * Time: O(n). Space: O(n).
 */

// @lc code=start
class Solution {
    public int longestArithmetic(int[] nums) {
        int n = nums.length;
        if (n <= 2) {
            return n;
        }

        int[] diff = new int[n - 1];
        for (int i = 0; i < n - 1; i++) {
            diff[i] = nums[i + 1] - nums[i];
        }

        int[] left = new int[n - 1];
        int[] right = new int[n - 1];
        for (int i = 0; i < n - 1; i++) {
            left[i] = right[i] = 1;
        }
        for (int i = 1; i < n - 1; i++) {
            if (diff[i] == diff[i - 1]) {
                left[i] = left[i - 1] + 1;
            }
        }
        for (int i = n - 3; i >= 0; i--) {
            if (diff[i] == diff[i + 1]) {
                right[i] = right[i + 1] + 1;
            }
        }

        int longestDiffRun = 1;
        for (int value : left) {
            longestDiffRun = Math.max(longestDiffRun, value);
        }
        int answer = Math.min(n, longestDiffRun + 2);

        for (int middle = 1; middle < n - 1; middle++) {
            int gap = nums[middle + 1] - nums[middle - 1];
            if ((gap & 1) != 0) {
                continue;
            }
            int common = gap / 2;
            int leftCount = middle - 2 >= 0 && diff[middle - 2] == common ? left[middle - 2] : 0;
            int rightIndex = middle + 1;
            int rightCount = rightIndex < diff.length && diff[rightIndex] == common ? right[rightIndex] : 0;
            answer = Math.max(answer, leftCount + 3 + rightCount);
        }
        return answer;
    }
}
// @lc code=end
