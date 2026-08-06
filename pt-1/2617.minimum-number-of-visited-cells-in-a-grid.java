/*
 * @lc app=leetcode id=2617 lang=java
 *
 * [2617] Minimum Number of Visited Cells in a Grid
 */

/*
 * Backward DP: {@code f(i,j)} = min visited cells from (i,j) to goal counting (i,j).
 * {@code f(i,j) = 1 + min(min row to the right, min column down)} with careful INF
 * handling for the goal cell. Segment trees per row and column for range min / point update.
 *
 * Time: O(m n (log m + log n)). Space: O(m n) for tree storage.
 * =============================================================================
 */

import java.util.Arrays;

// @lc code=start
class Solution {
    private static final class SegTree {
        private final int inf;
        private final int size;
        private final int[] t;

        SegTree(int n, int inf) {
            this.inf = inf;
            int s = 1;
            while (s < n) {
                s <<= 1;
            }
            this.size = s;
            this.t = new int[2 * s];
            Arrays.fill(t, inf);
        }

        void update(int pos, int val) {
            int i = pos + size;
            t[i] = val;
            i >>= 1;
            while (i > 0) {
                t[i] = Math.min(t[i << 1], t[(i << 1) | 1]);
                i >>= 1;
            }
        }

        int query(int l, int r) {
            if (l > r) {
                return inf;
            }
            l += size;
            r += size;
            int res = inf;
            while (l <= r) {
                if ((l & 1) == 1) {
                    res = Math.min(res, t[l]);
                    l++;
                }
                if ((r & 1) == 0) {
                    res = Math.min(res, t[r]);
                    r--;
                }
                l >>= 1;
                r >>= 1;
            }
            return res;
        }
    }

    public int minimumVisitedCells(int[][] grid) {
        int m = grid.length;
        int n = grid[0].length;
        int INF = 1_000_000_000;

        SegTree[] rows = new SegTree[m];
        SegTree[] cols = new SegTree[n];
        for (int i = 0; i < m; i++) {
            rows[i] = new SegTree(n, INF);
        }
        for (int j = 0; j < n; j++) {
            cols[j] = new SegTree(m, INF);
        }

        rows[m - 1].update(n - 1, 1);
        cols[n - 1].update(m - 1, 1);

        for (int i = m - 1; i >= 0; i--) {
            for (int j = n - 1; j >= 0; j--) {
                if (grid[i][j] == 0) {
                    continue;
                }
                int rMax = Math.min(n - 1, j + grid[i][j]);
                int dMax = Math.min(m - 1, i + grid[i][j]);
                int mr = rows[i].query(j + 1, rMax);
                int md = cols[j].query(i + 1, dMax);
                int cur = Math.min(rows[i].query(j, j), cols[j].query(i, i));
                int newVal;
                if (mr >= INF && md >= INF) {
                    newVal = cur;
                } else {
                    newVal = Math.min(cur, Math.min(mr, md) + 1);
                }
                rows[i].update(j, newVal);
                cols[j].update(i, newVal);
            }
        }

        int res = rows[0].query(0, 0);
        return res >= INF ? -1 : res;
    }
}
// @lc code=end
