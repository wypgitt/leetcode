/*
 * @lc app=leetcode id=3836 lang=java
 *
 * [3836] Maximum Score Using Exactly K Pairs
 *
 * Layered DP for selecting exactly p pairs from prefixes of nums1 and nums2.
 * cur[i][j] is the best score using p pairs from nums1[0..i) and nums2[0..j).
 * Either skip one side's last element or pair nums1[i-1] with nums2[j-1].
 *
 * Time: O(k n m). Space: O(n m).
 */

import java.util.Arrays;

// @lc code=start
class Solution {
    public long maxScore(int[] nums1, int[] nums2, int k) {
        int n = nums1.length;
        int m = nums2.length;
        long[][] prev = new long[n + 1][m + 1];
        long negInf = Long.MIN_VALUE / 4;

        for (int pairs = 1; pairs <= k; pairs++) {
            long[][] cur = new long[n + 1][m + 1];
            for (long[] row : cur) {
                Arrays.fill(row, negInf);
            }

            for (int i = pairs; i <= n; i++) {
                for (int j = pairs; j <= m; j++) {
                    long take = prev[i - 1][j - 1] + (long) nums1[i - 1] * nums2[j - 1];
                    cur[i][j] = Math.max(Math.max(cur[i - 1][j], cur[i][j - 1]), take);
                }
            }
            prev = cur;
        }
        return prev[n][m];
    }
}
// @lc code=end
