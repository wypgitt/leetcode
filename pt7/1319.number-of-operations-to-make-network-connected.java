/*
 * LeetCode 1319 - Number of Operations to Make Network Connected
 */
class Solution {
    public int makeConnected(int n, int[][] connections) {
        if (connections.length < n - 1) {
            return -1;
        }

        UnionFind unionFind = new UnionFind(n);
        int components = n;

        for (int[] connection : connections) {
            if (unionFind.union(connection[0], connection[1])) {
                components--;
            }
        }

        return components - 1;
    }

    private static class UnionFind {
        private final int[] parent;
        private final int[] rank;

        UnionFind(int size) {
            parent = new int[size];
            rank = new int[size];
            for (int i = 0; i < size; i++) {
                parent[i] = i;
            }
        }

        int find(int node) {
            if (parent[node] != node) {
                parent[node] = find(parent[node]);
            }
            return parent[node];
        }

        boolean union(int a, int b) {
            int rootA = find(a);
            int rootB = find(b);
            if (rootA == rootB) {
                return false;
            }

            if (rank[rootA] < rank[rootB]) {
                parent[rootA] = rootB;
            } else if (rank[rootA] > rank[rootB]) {
                parent[rootB] = rootA;
            } else {
                parent[rootB] = rootA;
                rank[rootA]++;
            }

            return true;
        }
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Any connected network of n nodes needs at least n - 1 cables. If there are
 * enough cables, extra cables inside connected components can be moved to join
 * components. The answer is therefore `numberOfComponents - 1`.
 *
 * Java data structures:
 * A Union-Find stores connected components. Path compression in `find` and
 * union by rank make operations nearly constant time.
 *
 * Edge cases:
 * - Fewer than n - 1 cables means impossible.
 * - Duplicate or redundant cables do not reduce components, but they serve as
 *   movable extras.
 * - n = 1 returns 0.
 *
 * Complexity:
 * Time O((n + e) alpha(n)), effectively linear.
 * Space O(n).
 */
