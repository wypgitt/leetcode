/*
 * @lc app=leetcode id=3772 lang=java
 *
 * [3772] Maximum Subgraph Score in a Tree
 *
 * Treat good nodes as +1 and others as -1. First compute down[u], the best
 * positive connected contribution from u's rooted subtree. Then reroot:
 * answer[child] = down[child] plus any positive parent-side contribution.
 *
 * Java note: adjacency is stored in ArrayList<Integer>[]; iterative traversal
 * avoids recursion-depth issues on large trees.
 *
 * Time: O(n). Space: O(n).
 */

import java.util.ArrayList;
import java.util.List;

// @lc code=start
class Solution {
    public int[] maxSubgraphScore(int n, int[][] edges, int[] good) {
        List<Integer>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }
        for (int[] edge : edges) {
            graph[edge[0]].add(edge[1]);
            graph[edge[1]].add(edge[0]);
        }

        int[] parent = new int[n];
        int[] order = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = -1;
        }
        int size = 0;
        order[size++] = 0;
        for (int i = 0; i < size; i++) {
            int node = order[i];
            for (int nei : graph[node]) {
                if (nei == parent[node]) {
                    continue;
                }
                parent[nei] = node;
                order[size++] = nei;
            }
        }

        int[] down = new int[n];
        for (int i = 0; i < n; i++) {
            down[i] = good[i] == 1 ? 1 : -1;
        }
        for (int i = n - 1; i >= 0; i--) {
            int node = order[i];
            for (int nei : graph[node]) {
                if (parent[nei] == node) {
                    down[node] += Math.max(0, down[nei]);
                }
            }
        }

        int[] answer = new int[n];
        answer[0] = down[0];
        for (int i = 0; i < n; i++) {
            int node = order[i];
            for (int nei : graph[node]) {
                if (parent[nei] != node) {
                    continue;
                }
                int withoutChild = answer[node] - Math.max(0, down[nei]);
                answer[nei] = down[nei] + Math.max(0, withoutChild);
            }
        }
        return answer;
    }
}
// @lc code=end
