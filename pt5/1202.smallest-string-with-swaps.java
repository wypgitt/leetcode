import java.util.*;

class Solution {
    public String smallestStringWithSwaps(String s, List<List<Integer>> pairs) {
        DSU dsu = new DSU(s.length());
        for (List<Integer> pair : pairs) {
            dsu.union(pair.get(0), pair.get(1));
        }

        Map<Integer, PriorityQueue<Character>> groups = new HashMap<>();
        for (int i = 0; i < s.length(); i++) {
            int root = dsu.find(i);
            groups.computeIfAbsent(root, key -> new PriorityQueue<>()).offer(s.charAt(i));
        }

        StringBuilder answer = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            answer.append(groups.get(dsu.find(i)).poll());
        }
        return answer.toString();
    }

    private static class DSU {
        int[] parent;
        int[] rank;

        DSU(int n) {
            parent = new int[n];
            rank = new int[n];
            for (int i = 0; i < n; i++) {
                parent[i] = i;
            }
        }

        int find(int x) {
            if (parent[x] != x) {
                parent[x] = find(parent[x]);
            }
            return parent[x];
        }

        void union(int a, int b) {
            int rootA = find(a);
            int rootB = find(b);
            if (rootA == rootB) {
                return;
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
        }
    }
}

