/*
 * @lc app=leetcode id=356 lang=java
 *
 * [356] Line Reflection
 *
 * The mirror axis is forced by the minimum and maximum x-coordinate:
 * doubledAxis = minX + maxX. Store all distinct points in a HashSet and check
 * that every point (x, y) has partner (doubledAxis - x, y).
 *
 * Java note: HashSet gives average O(1) membership checks. Points are encoded
 * as "x#y" strings to avoid writing a custom value class.
 *
 * Time: O(n). Space: O(n).
 */

import java.util.HashSet;
import java.util.Set;

// @lc code=start
class Solution {
    public boolean isReflected(int[][] points) {
        int minX = Integer.MAX_VALUE;
        int maxX = Integer.MIN_VALUE;
        Set<String> seen = new HashSet<>();

        for (int[] point : points) {
            int x = point[0];
            int y = point[1];
            minX = Math.min(minX, x);
            maxX = Math.max(maxX, x);
            seen.add(key(x, y));
        }

        int axisSum = minX + maxX;
        for (String encoded : seen) {
            int split = encoded.indexOf('#');
            int x = Integer.parseInt(encoded.substring(0, split));
            int y = Integer.parseInt(encoded.substring(split + 1));
            if (!seen.contains(key(axisSum - x, y))) {
                return false;
            }
        }
        return true;
    }

    private String key(int x, int y) {
        return x + "#" + y;
    }
}
// @lc code=end
