/*
 * @lc app=leetcode id=2613 lang=java
 *
 * [2613] Beautiful Pairs
 */

/*
 * Minimum Manhattan distance among pairs i < j; tie-break lexicographic (i, j).
 * Duplicate coordinates yield distance 0 — take lex-smallest (idx0, idx1) per group.
 * Otherwise divide & conquer on points sorted by x, merge with vertical strip sorted by y.
 *
 * Time: O(n log n). Space: O(n).
 * =============================================================================
 */

import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

// @lc code=start
class Solution {
    private static final long INF = (long) 1e18;

    public int[] beautifulPair(int[] nums1, int[] nums2) {
        int n = nums1.length;

        Map<Long, List<Integer>> groups = new HashMap<>();
        for (int i = 0; i < n; i++) {
            groups.computeIfAbsent(pack(nums1[i], nums2[i]), k -> new ArrayList<>()).add(i);
        }

        int[] bestDup = null;
        for (List<Integer> idxs : groups.values()) {
            if (idxs.size() >= 2) {
                int a = idxs.get(0);
                int b = idxs.get(1);
                if (bestDup == null || a < bestDup[0] || (a == bestDup[0] && b < bestDup[1])) {
                    bestDup = new int[] {a, b};
                }
            }
        }
        if (bestDup != null) {
            return bestDup;
        }

        int[][] pts = new int[n][3];
        for (int i = 0; i < n; i++) {
            pts[i][0] = nums1[i];
            pts[i][1] = nums2[i];
            pts[i][2] = i;
        }
        Arrays.sort(pts, (a, b) -> {
            if (a[0] != b[0]) {
                return Integer.compare(a[0], b[0]);
            }
            if (a[1] != b[1]) {
                return Integer.compare(a[1], b[1]);
            }
            return Integer.compare(a[2], b[2]);
        });

        long[] res = dfs(pts, 0, n - 1);
        return new int[] {(int) res[1], (int) res[2]};
    }

    private static long pack(int x, int y) {
        return (((long) x) << 32) | (y & 0xffffffffL);
    }

    private static int manhattan(int x1, int y1, int x2, int y2) {
        return Math.abs(x1 - x2) + Math.abs(y1 - y2);
    }

    private static boolean better(long d1, int i1, int j1, long d2, int i2, int j2) {
        if (d2 < d1) {
            return true;
        }
        if (d2 > d1) {
            return false;
        }
        return i2 < i1 || (i2 == i1 && j2 < j1);
    }

    /** Returns {d, pi, pj}. */
    private static long[] dfs(int[][] pts, int l, int r) {
        if (l >= r) {
            return new long[] {INF, -1, -1};
        }
        int m = (l + r) >>> 1;
        int xMid = pts[m][0];
        long[] left = dfs(pts, l, m);
        long[] right = dfs(pts, m + 1, r);
        long d = left[0];
        int a = (int) left[1];
        int b = (int) left[2];
        if (better(d, a, b, right[0], (int) right[1], (int) right[2])) {
            d = right[0];
            a = (int) right[1];
            b = (int) right[2];
        }

        List<int[]> strip = new ArrayList<>();
        for (int i = l; i <= r; i++) {
            if (Math.abs(pts[i][0] - xMid) <= d) {
                strip.add(pts[i]);
            }
        }
        strip.sort((p, q) -> Integer.compare(p[1], q[1]));
        int sz = strip.size();
        for (int i = 0; i < sz; i++) {
            int[] pi = strip.get(i);
            for (int j = i + 1; j < sz; j++) {
                int[] pj = strip.get(j);
                if (pj[1] - pi[1] > d) {
                    break;
                }
                int ii = pi[2];
                int jj = pj[2];
                int lo = Math.min(ii, jj);
                int hi = Math.max(ii, jj);
                int dist = manhattan(pi[0], pi[1], pj[0], pj[1]);
                if (better(d, a, b, dist, lo, hi)) {
                    d = dist;
                    a = lo;
                    b = hi;
                }
            }
        }
        return new long[] {d, a, b};
    }
}
// @lc code=end
