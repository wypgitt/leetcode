/*
 * @lc app=leetcode id=2608 lang=java
 *
 * [2608] Shortest Cycle in a Graph
 */

/*
 * For each source s, BFS gives distances. When visiting edge (u,v), if v was seen and
 * (v,u) is not the BFS tree edge back to parent ({@code dist[v] + 1 != dist[u]}), a
 * cycle of length {@code dist[u] + dist[v] + 1} is found. Take the minimum over all s.
 *
 * Time: O(n · (n + m)). Space: O(n + m).
 * =============================================================================
 */

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Deque;
import java.util.List;

// @lc code=start
class Solution {
    private static final int INF = 1_000_000_000;

    public int findShortestCycle(int n, int[][] edges) {
        List<Integer>[] g = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            g[i] = new ArrayList<>();
        }
        for (int[] e : edges) {
            int u = e[0];
            int v = e[1];
            g[u].add(v);
            g[v].add(u);
        }

        int ans = INF;
        for (int s = 0; s < n; s++) {
            ans = Math.min(ans, bfs(g, s, n));
        }
        return ans >= INF ? -1 : ans;
    }

    private int bfs(List<Integer>[] g, int src, int n) {
        int[] dist = new int[n];
        Arrays.fill(dist, -1);
        dist[src] = 0;
        Deque<Integer> q = new ArrayDeque<>();
        q.add(src);
        int best = INF;
        while (!q.isEmpty()) {
            int u = q.poll();
            for (int v : g[u]) {
                if (dist[v] == -1) {
                    dist[v] = dist[u] + 1;
                    q.add(v);
                } else if (dist[v] + 1 != dist[u]) {
                    best = Math.min(best, dist[u] + dist[v] + 1);
                }
            }
        }
        return best;
    }
}
// @lc code=end
