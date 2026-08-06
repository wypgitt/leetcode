/*
 * @lc app=leetcode id=3910 lang=java
 *
 * [3910] Count Connected Subgraphs with Even Node Sum
 *
 * n <= 13: enumerate masks, even sum filter, DFS connectivity with vis = fullMask ^ sub.
 */

// @lc code=start
class Solution {
    public int evenSumSubgraphs(int[] nums, int[][] edges) {
        int n = nums.length;
        int[][] g = new int[n][];
        int[] deg = new int[n];
        for (int[] e : edges) {
            deg[e[0]]++;
            deg[e[1]]++;
        }
        for (int i = 0; i < n; i++) {
            g[i] = new int[deg[i]];
        }
        int[] idx = new int[n];
        for (int[] e : edges) {
            int u = e[0];
            int v = e[1];
            g[u][idx[u]++] = v;
            g[v][idx[v]++] = u;
        }

        int full = (1 << n) - 1;
        int ans = 0;

        for (int sub = 1; sub <= full; sub++) {
            int s = 0;
            for (int i = 0; i < n; i++) {
                if (((sub >> i) & 1) == 1) {
                    s += nums[i];
                }
            }
            if ((s & 1) == 1) {
                continue;
            }
            int vis = full ^ sub;
            vis = dfs(highestBit(sub), g, vis);
            if (vis == full) {
                ans++;
            }
        }
        return ans;
    }

    private int highestBit(int sub) {
        return 31 - Integer.numberOfLeadingZeros(sub);
    }

    private int dfs(int u, int[][] g, int vis) {
        vis |= 1 << u;
        for (int v : g[u]) {
            if (((vis >> v) & 1) == 0) {
                vis = dfs(v, g, vis);
            }
        }
        return vis;
    }
}
// @lc code=end
