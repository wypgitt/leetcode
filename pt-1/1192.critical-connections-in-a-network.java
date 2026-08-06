/*
 * @lc app=leetcode id=1192 lang=java
 *
 * [1192] Critical Connections in a Network
 */

// @lc code=start
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    private int time;
    private int[] disc;
    private int[] low;
    private List<List<Integer>> bridges;
    private List<Integer>[] g;

    public List<List<Integer>> criticalConnections(int n, List<List<Integer>> connections) {
        g = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            g[i] = new ArrayList<>();
        }
        for (List<Integer> e : connections) {
            int a = e.get(0);
            int b = e.get(1);
            g[a].add(b);
            g[b].add(a);
        }
        disc = new int[n];
        low = new int[n];
        bridges = new ArrayList<>();
        time = 1;
        Arrays.fill(disc, 0);

        for (int i = 0; i < n; i++) {
            if (disc[i] == 0) {
                dfs(i, -1);
            }
        }
        bridges.sort((a, b) -> a.get(0) != b.get(0) ? Integer.compare(a.get(0), b.get(0)) : Integer.compare(a.get(1), b.get(1)));
        return bridges;
    }

    private void dfs(int u, int parent) {
        disc[u] = low[u] = time++;
        for (int v : g[u]) {
            if (v == parent) {
                continue;
            }
            if (disc[v] == 0) {
                dfs(v, u);
                low[u] = Math.min(low[u], low[v]);
                if (low[v] > disc[u]) {
                    int a = Math.min(u, v);
                    int b = Math.max(u, v);
                    bridges.add(Arrays.asList(a, b));
                }
            } else {
                low[u] = Math.min(low[u], disc[v]);
            }
        }
    }
}
// @lc code=end
