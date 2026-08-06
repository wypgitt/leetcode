/*
 * @lc app=leetcode id=3897 lang=java
 *
 * [3897] Maximum Value of Concatenated Binary Segments
 *
 * Sort segments by three-type comparator; accumulate value with powers of two mod MOD.
 */

import java.util.Arrays;
import java.util.Comparator;

// @lc code=start
class Solution {
    private static final int MOD = 1_000_000_007;

    public int maxValue(int[] nums1, int[] nums0) {
        int n = nums1.length;
        int[][] pairs = new int[n][2];
        int b = 0;
        for (int i = 0; i < n; i++) {
            pairs[i][0] = nums1[i];
            pairs[i][1] = nums0[i];
            b += nums1[i] + nums0[i];
        }

        Arrays.sort(
                pairs,
                Comparator.comparingInt((int[] p) -> group(p[0], p[1]))
                        .thenComparingInt((int[] p) -> key2(p[0], p[1]))
                        .thenComparingInt((int[] p) -> key3(p[0], p[1])));

        int[] pow2 = new int[b];
        pow2[0] = 1;
        for (int i = 1; i < b; i++) {
            pow2[i] = (int) ((pow2[i - 1] * 2L) % MOD);
        }

        int ans = 0;
        int bit = b - 1;
        for (int[] p : pairs) {
            int cnt1 = p[0];
            int cnt0 = p[1];
            while (cnt1 > 0) {
                ans = (ans + pow2[bit]) % MOD;
                bit--;
                cnt1--;
            }
            bit -= cnt0;
        }
        return ans;
    }

    private static int group(int x, int y) {
        if (y == 0) {
            return 0;
        }
        if (x > 0) {
            return 1;
        }
        return 2;
    }

    /** Middle key: (0,-x,0), (1,-x,y), (2,y,0). */
    private static int key2(int x, int y) {
        if (y == 0) {
            return -x;
        }
        if (x > 0) {
            return -x;
        }
        return y;
    }

    private static int key3(int x, int y) {
        if (y == 0) {
            return 0;
        }
        if (x > 0) {
            return y;
        }
        return 0;
    }
}
// @lc code=end
