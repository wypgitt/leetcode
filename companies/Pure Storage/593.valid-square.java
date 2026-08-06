import java.util.*;

/**
 * Algorithm:
 * A valid square has four equal nonzero side distances and two equal diagonal
 * distances, with each diagonal equal to twice a side distance. Compute all six
 * squared distances and sort them.
 *
 * Complexity:
 * Time O(1), space O(1).
 */
class Solution {
    public boolean validSquare(int[] p1, int[] p2, int[] p3, int[] p4) {
        int[][] points = {p1, p2, p3, p4};
        int[] dists = new int[6];
        int idx = 0;
        for (int i = 0; i < 4; i++) {
            for (int j = i + 1; j < 4; j++) {
                dists[idx++] = dist(points[i], points[j]);
            }
        }
        Arrays.sort(dists);
        return dists[0] > 0 &&
               dists[0] == dists[1] &&
               dists[1] == dists[2] &&
               dists[2] == dists[3] &&
               dists[4] == dists[5] &&
               dists[4] == 2 * dists[0];
    }

    private int dist(int[] a, int[] b) {
        int dx = a[0] - b[0];
        int dy = a[1] - b[1];
        return dx * dx + dy * dy;
    }
}

