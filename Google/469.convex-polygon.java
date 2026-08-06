/*
 * @lc app=leetcode id=469 lang=java
 *
 * [469] Convex Polygon
 *
 * For a polygon in order, all non-zero cross products of consecutive triples
 * must have the same sign. Collinear triples are ignored; the first non-zero
 * turn fixes the orientation.
 *
 * Time: O(n). Space: O(1).
 */

// @lc code=start
class Solution {
    public boolean isConvex(int[][] points) {
        int sign = 0;
        int n = points.length;

        for (int i = 0; i < n; i++) {
            long cross = cross(points[i], points[(i + 1) % n], points[(i + 2) % n]);
            if (cross == 0) {
                continue;
            }
            int current = cross > 0 ? 1 : -1;
            if (sign == 0) {
                sign = current;
            } else if (current != sign) {
                return false;
            }
        }
        return true;
    }

    private long cross(int[] a, int[] b, int[] c) {
        return (long) (b[0] - a[0]) * (c[1] - b[1])
                - (long) (b[1] - a[1]) * (c[0] - b[0]);
    }
}
// @lc code=end
