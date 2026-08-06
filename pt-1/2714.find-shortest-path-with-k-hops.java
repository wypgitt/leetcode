/*
 * @lc app=leetcode id=2714 lang=java
 *
 * [2714] Find Shortest Path with K Hops
 */

// @lc code=start
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;

class Solution {
    public int shortestPathWithHops(int n, int[][] edges, int source, int destination, int k) {
        List<List<int[]>> g = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            g.add(new ArrayList<>());
        }
        for (int[] e : edges) {
            int u = e[0];
            int v = e[1];
            int w = e[2];
            g.get(u).add(new int[] {v, w});
            g.get(v).add(new int[] {u, w});
        }
        long inf = 1_000_000_000_000_000_000L;
        long[][] dist = new long[n][k + 1];
        for (long[] row : dist) {
            Arrays.fill(row, inf);
        }
        dist[source][0] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        pq.offer(new long[] {0, source, 0});
        while (!pq.isEmpty()) {
            long[] cur = pq.poll();
            long du = cur[0];
            int u = (int) cur[1];
            int t = (int) cur[2];
            if (du != dist[u][t]) {
                continue;
            }
            for (int[] nx : g.get(u)) {
                int v = nx[0];
                int w = nx[1];
                long nd = du + w;
                if (nd < dist[v][t]) {
                    dist[v][t] = nd;
                    pq.offer(new long[] {nd, v, t});
                }
                if (t < k) {
                    nd = du;
                    if (nd < dist[v][t + 1]) {
                        dist[v][t + 1] = nd;
                        pq.offer(new long[] {nd, v, t + 1});
                    }
                }
            }
        }
        long ans = inf;
        for (int t = 0; t <= k; t++) {
            ans = Math.min(ans, dist[destination][t]);
        }
        return (int) ans;
    }
}
// @lc code=end
