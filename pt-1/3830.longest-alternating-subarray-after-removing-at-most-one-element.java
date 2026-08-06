/*
 * @lc app=leetcode id=3830 lang=java
 *
 * [3830] Longest Alternating Subarray After Removing at Most One Element
 *
 * Store the sign of every adjacent comparison. endLen[i] and startLen[i]
 * describe alternating runs ending/starting at each index. For each possible
 * removed middle element, bridge its neighbors and combine compatible left and
 * right runs.
 *
 * Time: O(n). Space: O(n).
 */

// @lc code=start
class Solution {
    public int longestAlternating(int[] nums) {
        int n = nums.length;
        if (n <= 1) {
            return n;
        }

        int[] sign = new int[n - 1];
        for (int i = 0; i < n - 1; i++) {
            sign[i] = cmp(nums[i], nums[i + 1]);
        }

        int[] endLen = new int[n];
        for (int i = 0; i < n; i++) {
            endLen[i] = 1;
        }
        for (int i = 1; i < n; i++) {
            if (sign[i - 1] == 0) {
                endLen[i] = 1;
            } else if (i >= 2 && sign[i - 2] == -sign[i - 1]) {
                endLen[i] = endLen[i - 1] + 1;
            } else {
                endLen[i] = 2;
            }
        }

        int[] startLen = new int[n];
        for (int i = 0; i < n; i++) {
            startLen[i] = 1;
        }
        for (int i = n - 2; i >= 0; i--) {
            if (sign[i] == 0) {
                startLen[i] = 1;
            } else if (i + 2 < n && sign[i] == -sign[i + 1]) {
                startLen[i] = startLen[i + 1] + 1;
            } else {
                startLen[i] = 2;
            }
        }

        int answer = 1;
        for (int value : endLen) {
            answer = Math.max(answer, value);
        }

        for (int removed = 1; removed < n - 1; removed++) {
            int bridge = cmp(nums[removed - 1], nums[removed + 1]);
            if (bridge == 0) {
                continue;
            }

            int left = removed >= 2 && sign[removed - 2] == -bridge ? endLen[removed - 1] : 1;
            int right = removed + 1 <= n - 2 && sign[removed + 1] == -bridge ? startLen[removed + 1] : 1;
            answer = Math.max(answer, left + right);
        }
        return answer;
    }

    private int cmp(int a, int b) {
        if (a < b) {
            return 1;
        }
        if (a > b) {
            return -1;
        }
        return 0;
    }
}
// @lc code=end
