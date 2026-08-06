/*
 * @lc app=leetcode id=2646 lang=java
 *
 * [2646] Minimize the Total Price of the Trips
 */

// @lc code=start
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    private List<Integer>[] g;
    private int[] freq;
    private int[] price;
    private int[][][] memo;

    public int minimumTotalPrice(int n, int[][] edges, int[] price, int[][] trips) {
        g = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            g[i] = new ArrayList<>();
        }
        for (int[] e : edges) {
            g[e[0]].add(e[1]);
            g[e[1]].add(e[0]);
        }
        this.price = price;
        freq = new int[n];
        for (int[] t : trips) {
            markPath(t[0], t[1]);
        }
        memo = new int[n][n + 1][2];
        for (int[][] a : memo) {
            for (int[] b : a) {
                Arrays.fill(b, -1);
            }
        }
        return dfs(0, -1, 0);
    }

    private void markPath(int start, int end) {
        List<Integer> path = new ArrayList<>();
        dfsPath(start, -1, end, path);
    }

    private boolean dfsPath(int u, int parent, int end, List<Integer> path) {
        path.add(u);
        if (u == end) {
            for (int x : path) {
                freq[x]++;
            }
            path.remove(path.size() - 1);
            return true;
        }
        for (int v : g[u]) {
            if (v != parent && dfsPath(v, u, end, path)) {
                path.remove(path.size() - 1);
                return true;
            }
        }
        path.remove(path.size() - 1);
        return false;
    }

    private int dfs(int u, int parent, int parentHalved) {
        int pi = parent + 1;
        int ph = parentHalved;
        if (memo[u][pi][ph] != -1) {
            return memo[u][pi][ph];
        }
        int payFull = price[u] * freq[u];
        for (int v : g[u]) {
            if (v != parent) {
                payFull += dfs(v, u, 0);
            }
        }
        if (parentHalved == 1) {
            return memo[u][pi][ph] = payFull;
        }
        int payHalf = (price[u] / 2) * freq[u];
        for (int v : g[u]) {
            if (v != parent) {
                payHalf += dfs(v, u, 1);
            }
        }
        return memo[u][pi][ph] = Math.min(payFull, payHalf);
    }
}
// @lc code=end
