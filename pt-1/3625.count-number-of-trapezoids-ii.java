/*
 * @lc app=leetcode id=3625 lang=java
 *
 * [3625] Count Number of Trapezoids II
 *
 * Count pairs of segments that lie on different parallel lines; each such pair
 * can be the two bases of a trapezoid. Parallelograms are counted twice by
 * choosing either opposite side pair, so subtract the number of parallelograms,
 * detected by equal diagonal midpoints and non-collinear diagonals.
 *
 * Java note: HashMap groups normalized slope keys and doubled midpoint keys.
 * Normalizing (dx, dy) by gcd gives a canonical direction for parallel checks.
 *
 * Time: O(n^2). Space: O(n^2).
 */

import java.util.HashMap;
import java.util.Map;

// @lc code=start
class Solution {
    public int countTrapezoids(int[][] points) {
        Map<String, Map<Long, Integer>> linesBySlope = new HashMap<>();
        Map<String, MidpointGroup> midpointGroups = new HashMap<>();

        int n = points.length;
        for (int i = 0; i < n; i++) {
            int x1 = points[i][0];
            int y1 = points[i][1];
            for (int j = i + 1; j < n; j++) {
                int x2 = points[j][0];
                int y2 = points[j][1];
                int[] dir = direction(x2 - x1, y2 - y1);
                String slopeKey = dir[0] + "#" + dir[1];

                long lineConstant = (long) dir[1] * x1 - (long) dir[0] * y1;
                linesBySlope.computeIfAbsent(slopeKey, unused -> new HashMap<>())
                        .merge(lineConstant, 1, Integer::sum);

                String midpointKey = (x1 + x2) + "#" + (y1 + y2);
                MidpointGroup group = midpointGroups.computeIfAbsent(midpointKey, unused -> new MidpointGroup());
                group.total++;
                group.slopeCounts.merge(slopeKey, 1, Integer::sum);
            }
        }

        long parallelSidePairs = 0;
        for (Map<Long, Integer> lineCounts : linesBySlope.values()) {
            long previous = 0;
            for (int count : lineCounts.values()) {
                parallelSidePairs += previous * count;
                previous += count;
            }
        }

        long parallelograms = 0;
        for (MidpointGroup group : midpointGroups.values()) {
            long current = (long) group.total * (group.total - 1) / 2;
            for (int sameSlope : group.slopeCounts.values()) {
                current -= (long) sameSlope * (sameSlope - 1) / 2;
            }
            parallelograms += current;
        }

        return (int) (parallelSidePairs - parallelograms);
    }

    private int[] direction(int dx, int dy) {
        int g = gcd(Math.abs(dx), Math.abs(dy));
        dx /= g;
        dy /= g;
        if (dx < 0 || (dx == 0 && dy < 0)) {
            dx = -dx;
            dy = -dy;
        }
        return new int[] {dx, dy};
    }

    private int gcd(int a, int b) {
        while (b != 0) {
            int t = a % b;
            a = b;
            b = t;
        }
        return a;
    }

    private static class MidpointGroup {
        int total;
        Map<String, Integer> slopeCounts = new HashMap<>();
    }
}
// @lc code=end
