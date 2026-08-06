/*
 * @lc app=leetcode id=3873 lang=java
 *
 * [3873] Maximum Points Activated with One Addition
 *
 * Bipartite connectivity on (x, y+M) edges; answer = largest + second largest component size + 1.
 * M must exceed coordinate range; use long for DSU keys (3e9 does not fit in int).
 */

import java.util.HashMap;
import java.util.Map;

// @lc code=start
class UnionFind {
    private final Map<Long, Long> p = new HashMap<>();
    private final Map<Long, Integer> sz = new HashMap<>();

    long find(long x) {
        if (!p.containsKey(x)) {
            p.put(x, x);
            sz.put(x, 1);
        }
        long px = p.get(x);
        if (px != x) {
            long r = find(px);
            p.put(x, r);
            return r;
        }
        return x;
    }

    void union(long a, long b) {
        long pa = find(a);
        long pb = find(b);
        if (pa == pb) {
            return;
        }
        int sa = sz.get(pa);
        int sb = sz.get(pb);
        if (sa > sb) {
            p.put(pb, pa);
            sz.put(pa, sa + sb);
        } else {
            p.put(pa, pb);
            sz.put(pb, sa + sb);
        }
    }
}

class Solution {
    private static final long M = 3_000_000_000L;

    public int maxActivated(int[][] points) {
        UnionFind uf = new UnionFind();
        for (int[] pt : points) {
            uf.union(pt[0], pt[1] + M);
        }
        Map<Long, Integer> cnt = new HashMap<>();
        for (int[] pt : points) {
            int x = pt[0];
            long r = uf.find(x);
            cnt.merge(r, 1, Integer::sum);
        }
        int mx1 = 0;
        int mx2 = 0;
        for (int v : cnt.values()) {
            if (v > mx1) {
                mx2 = mx1;
                mx1 = v;
            } else if (v > mx2) {
                mx2 = v;
            }
        }
        return mx1 + mx2 + 1;
    }
}
// @lc code=end
