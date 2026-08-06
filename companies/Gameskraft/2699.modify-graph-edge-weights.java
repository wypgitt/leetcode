/*
 * @lc app=leetcode id=2699 lang=java
 *
 * [2699] Modify Graph Edge Weights
 */

// @lc code=start
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;

class Solution {
    private static final int INF_EDGE = 2_000_000_000;
    private int n;
    private int[][] graphEdges;
    private int source;
    private int destination;

    public int[][] modifiedGraphEdges(int n, int[][] edges, int source, int destination, int target) {
        this.n = n;
        this.graphEdges = edges;
        this.source = source;
        this.destination = destination;

        int d = dijkstra();
        if (d < target) {
            return new int[0][0];
        }

        boolean ok = d == target;
        for (int[] e : edges) {
            if (e[2] > 0) {
                continue;
            }
            if (ok) {
                e[2] = INF_EDGE;
                continue;
            }
            e[2] = 1;
            d = dijkstra();
            if (d <= target) {
                ok = true;
                e[2] += target - d;
            }
        }

        return ok ? edges : new int[0][0];
    }

    private int dijkstra() {
        List<List<int[]>> g = new ArrayList<>();
        for (int i = 0; i < n; i++) {
            g.add(new ArrayList<>());
        }
        for (int[] e : graphEdges) {
            int a = e[0];
            int b = e[1];
            int w = e[2];
            if (w == -1) {
                continue;
            }
            g.get(a).add(new int[] {b, w});
            g.get(b).add(new int[] {a, w});
        }
        long[] dist = new long[n];
        Arrays.fill(dist, Long.MAX_VALUE / 4);
        dist[source] = 0;
        PriorityQueue<long[]> pq = new PriorityQueue<>((u, v) -> Long.compare(u[0], v[0]));
        pq.offer(new long[] {0, source});
        while (!pq.isEmpty()) {
            long[] cur = pq.poll();
            long du = cur[0];
            int u = (int) cur[1];
            if (du != dist[u]) {
                continue;
            }
            for (int[] nx : g.get(u)) {
                int v = nx[0];
                int w = nx[1];
                long nd = du + w;
                if (nd < dist[v]) {
                    dist[v] = nd;
                    pq.offer(new long[] {nd, v});
                }
            }
        }
        return (int) dist[destination];
    }
}
// @lc code=end
