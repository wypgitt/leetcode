import java.util.*;

class Solution {
    @SuppressWarnings("unchecked")
    public int[] shortestAlternatingPaths(int n, int[][] redEdges, int[][] blueEdges) {
        List<Integer>[][] graph = new ArrayList[2][n];
        for (int color = 0; color < 2; color++) {
            for (int node = 0; node < n; node++) {
                graph[color][node] = new ArrayList<>();
            }
        }

        for (int[] edge : redEdges) {
            graph[0][edge[0]].add(edge[1]);
        }
        for (int[] edge : blueEdges) {
            graph[1][edge[0]].add(edge[1]);
        }

        int[] answer = new int[n];
        Arrays.fill(answer, -1);
        boolean[][] visited = new boolean[n][2];
        Queue<int[]> queue = new ArrayDeque<>();
        queue.offer(new int[] {0, 0, 0});
        queue.offer(new int[] {0, 1, 0});
        visited[0][0] = true;
        visited[0][1] = true;

        while (!queue.isEmpty()) {
            int[] state = queue.poll();
            int node = state[0];
            int lastColor = state[1];
            int distance = state[2];

            if (answer[node] == -1) {
                answer[node] = distance;
            }

            int nextColor = 1 - lastColor;
            for (int neighbor : graph[nextColor][node]) {
                if (!visited[neighbor][nextColor]) {
                    visited[neighbor][nextColor] = true;
                    queue.offer(new int[] {neighbor, nextColor, distance + 1});
                }
            }
        }

        return answer;
    }
}
