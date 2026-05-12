import java.util.*;

class Solution {
    public int minimumCost(int n, int[][] connections) {
        if (n == 1) {
            return 0;
        }

        Arrays.sort(connections, Comparator.comparingInt(edge -> edge[2]));
        DSU dsu = new DSU(n + 1);
        int total = 0;
        int used = 0;

        for (int[] edge : connections) {
            if (dsu.union(edge[0], edge[1])) {
                total += edge[2];
                used++;
                if (used == n - 1) {
                    return total;
                }
            }
        }

        return -1;
    }

    private static class DSU {
        int[] parent;
        int[] rank;

        DSU(int size) {
            parent = new int[size];
            rank = new int[size];
            for (int i = 0; i < size; i++) {
                parent[i] = i;
            }
        }

        int find(int x) {
            if (parent[x] != x) {
                parent[x] = find(parent[x]);
            }
            return parent[x];
        }

        boolean union(int a, int b) {
            int rootA = find(a);
            int rootB = find(b);
            if (rootA == rootB) {
                return false;
            }
            if (rank[rootA] < rank[rootB]) {
                int temp = rootA;
                rootA = rootB;
                rootB = temp;
            }
            parent[rootB] = rootA;
            if (rank[rootA] == rank[rootB]) {
                rank[rootA]++;
            }
            return true;
        }
    }
}

