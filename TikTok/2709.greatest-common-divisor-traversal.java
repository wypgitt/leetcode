/*
 * @lc app=leetcode id=2709 lang=java
 *
 * [2709] Greatest Common Divisor Traversal
 */

// @lc code=start
class Solution {
    private static final int MX = 100_001;
    private static final int[][] PF = buildDistinctPrimeFactors(MX);

    private static int[][] buildDistinctPrimeFactors(int mx) {
        int[][] pf = new int[mx][];
        pf[0] = new int[0];
        pf[1] = new int[0];
        int[] tmp = new int[32];
        for (int x = 2; x < mx; x++) {
            int v = x;
            int cnt = 0;
            for (int d = 2; d * d <= v; d++) {
                if (v % d == 0) {
                    tmp[cnt++] = d;
                    while (v % d == 0) {
                        v /= d;
                    }
                }
            }
            if (v > 1) {
                tmp[cnt++] = v;
            }
            pf[x] = java.util.Arrays.copyOf(tmp, cnt);
        }
        return pf;
    }

    public boolean canTraverseAllPairs(int[] nums) {
        int n = nums.length;
        if (n == 1) {
            return true;
        }
        int m = 0;
        for (int x : nums) {
            m = Math.max(m, x);
        }
        UnionFind uf = new UnionFind(n + m + 1);
        for (int i = 0; i < n; i++) {
            int x = nums[i];
            for (int p : PF[x]) {
                uf.union(i, n + p);
            }
        }
        int r0 = uf.find(0);
        for (int i = 1; i < n; i++) {
            if (uf.find(i) != r0) {
                return false;
            }
        }
        return true;
    }

    private static class UnionFind {
        private final int[] p;
        private final int[] sz;

        UnionFind(int n) {
            p = new int[n];
            sz = new int[n];
            for (int i = 0; i < n; i++) {
                p[i] = i;
                sz[i] = 1;
            }
        }

        int find(int x) {
            if (p[x] != x) {
                p[x] = find(p[x]);
            }
            return p[x];
        }

        void union(int a, int b) {
            int pa = find(a);
            int pb = find(b);
            if (pa == pb) {
                return;
            }
            if (sz[pa] < sz[pb]) {
                int t = pa;
                pa = pb;
                pb = t;
            }
            p[pb] = pa;
            sz[pa] += sz[pb];
        }
    }
}
// @lc code=end
