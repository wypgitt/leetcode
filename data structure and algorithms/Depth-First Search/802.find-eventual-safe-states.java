import java.util.*;

/**
 * Algorithm:
 * DFS with colors: 0 unvisited, 1 currently visiting, 2 proven safe. A node is
 * safe only if every outgoing neighbor is safe. Encountering a visiting node
 * detects a cycle and returns false.
 *
 * Java data structures:
 * int[] color stores the DFS state compactly.
 *
 * Complexity:
 * Time O(V + E), space O(V) for color and recursion stack.
 */
class Solution {
    private int[][] graph;
    private int[] color;

    public List<Integer> eventualSafeNodes(int[][] graph) {
        this.graph = graph;
        this.color = new int[graph.length];
        List<Integer> ans = new ArrayList<>();
        for (int i = 0; i < graph.length; i++) {
            if (dfs(i)) {
                ans.add(i);
            }
        }
        return ans;
    }

    private boolean dfs(int node) {
        if (color[node] != 0) {
            return color[node] == 2;
        }
        color[node] = 1;
        for (int nei : graph[node]) {
            if (!dfs(nei)) {
                return false;
            }
        }
        color[node] = 2;
        return true;
    }
}

