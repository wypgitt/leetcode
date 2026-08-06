/*
 * @lc app=leetcode id=3887 lang=java
 *
 * [3887] Incremental Even-Weighted Cycle Queries
 *
 * DSU with XOR parity to root (GF(2)); add edge if consistent.
 */

// @lc code=start
class DSU {
    private final int[] p;
    private final int[] xw;

    DSU(int n) {
        p = new int[n];
        xw = new int[n];
        for (int i = 0; i < n; i++) {
            p[i] = i;
        }
    }

    int find(int a) {
        if (p[a] != a) {
            int orig = p[a];
            int root = find(orig);
            xw[a] ^= xw[orig];
            p[a] = root;
        }
        return p[a];
    }

    /** Returns true if edge can be added (cycle XOR 0 when same component). */
    boolean union(int u, int v, int w) {
        int pu = find(u);
        int pv = find(v);
        int xu = xw[u];
        int xv = xw[v];
        if (pu == pv) {
            return (xu ^ xv) == w;
        }
        p[pu] = pv;
        xw[pu] = xu ^ xv ^ w;
        return true;
    }
}

class Solution {
    public int numberOfEdgesAdded(int n, int[][] edges) {
        DSU dsu = new DSU(n);
        int ans = 0;
        for (int[] e : edges) {
            if (dsu.union(e[0], e[1], e[2])) {
                ans++;
            }
        }
        return ans;
    }
}
// @lc code=end
