import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.List;
import java.util.Queue;

class Solution {
    public int treeDiameter(int[][] edges) {
        if (edges.length == 0) {
            return 0;
        }

        int n = edges.length + 1;
        List<Integer>[] graph = new ArrayList[n];
        for (int i = 0; i < n; i++) {
            graph[i] = new ArrayList<>();
        }
        for (int[] edge : edges) {
            graph[edge[0]].add(edge[1]);
            graph[edge[1]].add(edge[0]);
        }

        int endpoint = farthest(graph, 0)[0];
        return farthest(graph, endpoint)[1];
    }

    private int[] farthest(List<Integer>[] graph, int start) {
        Queue<int[]> queue = new ArrayDeque<>();
        boolean[] seen = new boolean[graph.length];
        queue.offer(new int[] {start, 0});
        seen[start] = true;

        int farNode = start;
        int farDist = 0;
        while (!queue.isEmpty()) {
            int[] cur = queue.poll();
            if (cur[1] > farDist) {
                farNode = cur[0];
                farDist = cur[1];
            }
            for (int next : graph[cur[0]]) {
                if (!seen[next]) {
                    seen[next] = true;
                    queue.offer(new int[] {next, cur[1] + 1});
                }
            }
        }

        return new int[] {farNode, farDist};
    }
}

/*
Explanation

In any tree, if we start from an arbitrary node and find the farthest node A,
A is an endpoint of the diameter. A second BFS from A gives the diameter
length.

The adjacency-list array is the natural Java representation for a tree with
node ids 0..n-1. BFS uses an ArrayDeque queue and a boolean visited array.

Edge cases: a single-node tree has diameter 0; a chain returns n - 1; a star
returns 2.

Time complexity: O(n), two BFS traversals.
Space complexity: O(n).
*/
