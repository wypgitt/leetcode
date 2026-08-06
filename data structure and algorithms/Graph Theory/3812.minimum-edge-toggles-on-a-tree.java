/*
 * @lc app=leetcode id=3812 lang=java
 *
 * [3812] Minimum Edge Toggles on a Tree
 *
 * need[u] says whether node u currently differs from target. Process leaves
 * upward; if child u still needs a flip, toggle the edge to its parent, which
 * fixes u and flips the parent's need. The root must end fixed.
 *
 * Java note: each adjacency entry stores neighbor and original edge index so
 * the sorted answer can return edge IDs.
 *
 * Time: O(n log n) because of final sorting. Space: O(n).
 */

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

// @lc code=start
class Solution {
    public int[] minimumFlips(int n, int[][] edges, String start, String target) {
        List<int[]>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }
        for (int i = 0; i < edges.length; i++) {
            int u = edges[i][0];
            int v = edges[i][1];
            graph[u].add(new int[] {v, i});
            graph[v].add(new int[] {u, i});
        }

        int[] parent = new int[n];
        int[] parentEdge = new int[n];
        int[] order = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = -1;
            parentEdge[i] = -1;
        }
        int size = 0;
        order[size++] = 0;
        for (int i = 0; i < size; i++) {
            int node = order[i];
            for (int[] edge : graph[node]) {
                int nei = edge[0];
                if (nei == parent[node]) {
                    continue;
                }
                parent[nei] = node;
                parentEdge[nei] = edge[1];
                order[size++] = nei;
            }
        }

        int[] need = new int[n];
        for (int i = 0; i < n; i++) {
            need[i] = start.charAt(i) == target.charAt(i) ? 0 : 1;
        }

        List<Integer> answer = new ArrayList<>();
        for (int i = n - 1; i >= 1; i--) {
            int node = order[i];
            if (need[node] == 1) {
                answer.add(parentEdge[node]);
                need[node] ^= 1;
                need[parent[node]] ^= 1;
            }
        }
        if (need[0] == 1) {
            return new int[] {-1};
        }

        Collections.sort(answer);
        int[] out = new int[answer.size()];
        for (int i = 0; i < answer.size(); i++) {
            out[i] = answer.get(i);
        }
        return out;
    }
}
// @lc code=end
