/*
 * @lc app=leetcode id=391 lang=java
 *
 * [391] Perfect Rectangle
 *
 * A perfect cover has total small-rectangle area equal to bounding-box area,
 * and every internal corner appears an even number of times. Toggle each corner
 * in a set; only the four bounding corners should remain.
 *
 * Java note: HashSet<String> is a compact point set representation.
 *
 * Time: O(n). Space: O(n).
 */

import java.util.HashSet;
import java.util.Set;

// @lc code=start
class Solution {
    public boolean isRectangleCover(int[][] rectangles) {
        int minX = Integer.MAX_VALUE;
        int minY = Integer.MAX_VALUE;
        int maxX = Integer.MIN_VALUE;
        int maxY = Integer.MIN_VALUE;
        long totalArea = 0;
        Set<String> corners = new HashSet<>();

        for (int[] r : rectangles) {
            int x1 = r[0], y1 = r[1], x2 = r[2], y2 = r[3];
            minX = Math.min(minX, x1);
            minY = Math.min(minY, y1);
            maxX = Math.max(maxX, x2);
            maxY = Math.max(maxY, y2);
            totalArea += (long) (x2 - x1) * (y2 - y1);

            toggle(corners, x1, y1);
            toggle(corners, x1, y2);
            toggle(corners, x2, y1);
            toggle(corners, x2, y2);
        }

        long boundingArea = (long) (maxX - minX) * (maxY - minY);
        if (totalArea != boundingArea || corners.size() != 4) {
            return false;
        }
        return corners.contains(key(minX, minY))
                && corners.contains(key(minX, maxY))
                && corners.contains(key(maxX, minY))
                && corners.contains(key(maxX, maxY));
    }

    private void toggle(Set<String> set, int x, int y) {
        String key = key(x, y);
        if (!set.add(key)) {
            set.remove(key);
        }
    }

    private String key(int x, int y) {
        return x + "#" + y;
    }
}
// @lc code=end
