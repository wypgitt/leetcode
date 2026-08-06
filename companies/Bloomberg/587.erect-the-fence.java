/*
 * @lc app=leetcode id=587 lang=java
 *
 * [587] Erect the Fence
 *
 * Andrew's monotonic chain convex hull. Sort points, build lower and upper
 * hulls, and pop only on clockwise turns so collinear boundary points stay on
 * the fence. Use a set to remove duplicate endpoints.
 *
 * Time: O(n log n). Space: O(n).
 */

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

// @lc code=start
class Solution {
    public int[][] outerTrees(int[][] trees) {
        int[][] points = trees.clone();
        Arrays.sort(points, (a, b) -> a[0] == b[0] ? Integer.compare(a[1], b[1]) : Integer.compare(a[0], b[0]));
        if (points.length <= 3) {
            return points;
        }

        List<int[]> lower = new ArrayList<>();
        for (int[] point : points) {
            while (lower.size() >= 2 && cross(lower.get(lower.size() - 2), lower.get(lower.size() - 1), point) < 0) {
                lower.remove(lower.size() - 1);
            }
            lower.add(point);
        }

        List<int[]> upper = new ArrayList<>();
        for (int i = points.length - 1; i >= 0; i--) {
            int[] point = points[i];
            while (upper.size() >= 2 && cross(upper.get(upper.size() - 2), upper.get(upper.size() - 1), point) < 0) {
                upper.remove(upper.size() - 1);
            }
            upper.add(point);
        }

        Set<String> seen = new HashSet<>();
        List<int[]> answer = new ArrayList<>();
        for (int[] point : lower) {
            addPoint(answer, seen, point);
        }
        for (int[] point : upper) {
            addPoint(answer, seen, point);
        }
        return answer.toArray(new int[answer.size()][]);
    }

    private long cross(int[] a, int[] b, int[] c) {
        return (long) (b[0] - a[0]) * (c[1] - a[1])
                - (long) (b[1] - a[1]) * (c[0] - a[0]);
    }

    private void addPoint(List<int[]> answer, Set<String> seen, int[] point) {
        String key = point[0] + "#" + point[1];
        if (seen.add(key)) {
            answer.add(new int[] {point[0], point[1]});
        }
    }
}
// @lc code=end
