/*
 * @lc app=leetcode id=2612 lang=java
 *
 * [2612] Minimum Reverse Operations
 */

/*
 * BFS on positions; one reverse of length k maps u to v in an arithmetic progression
 * (step 2) inside [L, R]. Union-Find with {@code right} jump skips visited indices
 * so each position is processed amortized O(α(n)).
 *
 * Time: ~O(n α(n)). Space: O(n).
 * =============================================================================
 */

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Deque;
import java.util.List;

// @lc code=start
class Solution {

    private static final class UnionFind {
        private final int[] parent;
        private final int[] rank;
        private final int[] right;

        UnionFind(int n) {
            parent = new int[n];
            rank = new int[n];
            right = new int[n];
            for (int i = 0; i < n; i++) {
                parent[i] = i;
                right[i] = i;
            }
        }

        int find(int x) {
            int root = x;
            while (parent[root] != root) {
                root = parent[root];
            }
            while (parent[x] != x) {
                int nx = parent[x];
                parent[x] = root;
                x = nx;
            }
            return root;
        }

        void union(int x, int y) {
            int px = find(x);
            int py = find(y);
            if (px == py) {
                return;
            }
            if (rank[px] > rank[py]) {
                int tmp = px;
                px = py;
                py = tmp;
            }
            parent[px] = py;
            if (rank[px] == rank[py]) {
                rank[py]++;
            }
            right[py] = Math.max(right[px], right[py]);
        }

        int rightSet(int x) {
            return right[find(x)];
        }
    }

    public int[] minReverseOperations(int n, int p, int[] banned, int k) {
        boolean[] bannedOn = new boolean[n];
        for (int i : banned) {
            bannedOn[i] = true;
        }

        int[] ans = new int[n];
        Arrays.fill(ans, -1);
        ans[p] = 0;

        UnionFind uf = new UnionFind(n + 2);
        uf.union(p, p + 2);

        Deque<Integer> q = new ArrayDeque<>();
        q.add(p);
        int step = 1;
        while (!q.isEmpty()) {
            List<Integer> nxt = new ArrayList<>();
            for (int u : q) {
                int left = Math.max(u - k + 1, k - 1 - u);
                int right = Math.min(u + k - 1, n - 1 - (u - (n - k)));
                int x = uf.rightSet(left);
                while (x <= right) {
                    if (!bannedOn[x]) {
                        ans[x] = step;
                        nxt.add(x);
                    }
                    uf.union(x, x + 2);
                    x = uf.rightSet(x);
                }
            }
            q = new ArrayDeque<>(nxt);
            step++;
        }
        return ans;
    }
}
// @lc code=end
