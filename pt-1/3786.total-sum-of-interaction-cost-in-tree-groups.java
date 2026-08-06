/*
 * @lc app=leetcode id=3786 lang=java
 *
 * [3786] Total Sum of Interaction Cost in Tree Groups
 *
 * For each edge and each label, pairs separated by that edge contribute one to
 * their distance. During a postorder traversal, count labels inside every child
 * subtree; contribution is inside * (total[label] - inside).
 *
 * Java note: labels are bounded by 20, so int[n][21] is faster and simpler
 * than a map per node.
 *
 * Time: O(20n). Space: O(20n).
 */

import java.util.ArrayList;
import java.util.List;

// @lc code=start
class Solution {
    public long interactionCosts(int n, int[][] edges, int[] group) {
        if (n == 1) {
            return 0;
        }

        List<Integer>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }
        for (int[] edge : edges) {
            graph[edge[0]].add(edge[1]);
            graph[edge[1]].add(edge[0]);
        }

        int[] total = new int[21];
        for (int label : group) {
            total[label]++;
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

        int[][] subtree = new int[n][21];
        long answer = 0;
        for (int i = n - 1; i >= 0; i--) {
            int node = order[i];
            subtree[node][group[node]]++;
            if (node != 0) {
                for (int label = 1; label <= 20; label++) {
                    int inside = subtree[node][label];
                    answer += (long) inside * (total[label] - inside);
                    subtree[parent[node]][label] += inside;
                }
            }
        }
        return answer;
    }
}
// @lc code=end
