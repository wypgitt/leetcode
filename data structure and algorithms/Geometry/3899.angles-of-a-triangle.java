/*
 * @lc app=leetcode id=3899 lang=java
 *
 * [3899] Angles of a Triangle
 *
 * Sort side lengths, reject invalid triangles, then use the law of cosines for
 * each opposite side. Clamp cosine into [-1, 1] to avoid floating-point drift.
 *
 * Time: O(1). Space: O(1).
 */

import java.util.Arrays;

// @lc code=start
class Solution {
    public double[] internalAngles(int[] sides) {
        int[] sorted = sides.clone();
        Arrays.sort(sorted);
        int a = sorted[0];
        int b = sorted[1];
        int c = sorted[2];
        if (a + b <= c) {
            return new double[0];
        }

        double[] angles = {
            angle(a, b, c),
            angle(b, a, c),
            angle(c, a, b)
        };
        Arrays.sort(angles);
        return angles;
    }

    private double angle(int opposite, int side1, int side2) {
        double cos = ((double) side1 * side1 + (double) side2 * side2 - (double) opposite * opposite)
                / (2.0 * side1 * side2);
        cos = Math.max(-1.0, Math.min(1.0, cos));
        return Math.toDegrees(Math.acos(cos));
    }
}
// @lc code=end
