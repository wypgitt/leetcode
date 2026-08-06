/*
 * @lc app=leetcode id=2642 lang=java
 *
 * [2642] Design Graph With Shortest Path Calculator
 */

/*
 * Directed nonnegative weights: Dijkstra from {@code node1} on each shortest-path query.
 * Adjacency lists; min-heap by tentative distance; early exit when {@code node2} is popped.
 *
 * Time: O((V + E) log V) per query. Space: O(V + E).
 * =============================================================================
 */

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.PriorityQueue;

// @lc code=start
class Graph {
    private final int n;
    private final List<int[]>[] g;

    @SuppressWarnings("unchecked")
    public Graph(int n, int[][] edges) {
        this.n = n;
        this.g = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            g[i] = new ArrayList<>();
        }
        for (int[] e : edges) {
            g[e[0]].add(new int[] {e[1], e[2]});
        }
    }

    public void addEdge(int[] edge) {
        g[edge[0]].add(new int[] {edge[1], edge[2]});
    }

    public int shortestPath(int node1, int node2) {
        if (node1 == node2) {
            return 0;
        }
        long[] dist = new long[n];
        Arrays.fill(dist, Long.MAX_VALUE / 4);
        dist[node1] = 0;
        PriorityQueue<long[]> heap = new PriorityQueue<>((a, b) -> Long.compare(a[0], b[0]));
        heap.offer(new long[] {0, node1});
        while (!heap.isEmpty()) {
            long[] top = heap.poll();
            long d = top[0];
            int u = (int) top[1];
            if (d > dist[u]) {
                continue;
            }
            if (u == node2) {
                return (int) d;
            }
            for (int[] e : g[u]) {
                int v = e[0];
                int w = e[1];
                long nd = d + w;
                if (nd < dist[v]) {
                    dist[v] = nd;
                    heap.offer(new long[] {nd, v});
                }
            }
        }
        return -1;
    }
}
// @lc code=end
