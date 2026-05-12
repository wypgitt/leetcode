import java.util.*;

class Solution {
    public int maxDistance(int[][] grid) {
        int n = grid.length;
        Queue<int[]> queue = new ArrayDeque<>();

        for (int r = 0; r < n; r++) {
            for (int c = 0; c < n; c++) {
                if (grid[r][c] == 1) {
                    queue.offer(new int[] {r, c});
                }
            }
        }

        if (queue.isEmpty() || queue.size() == n * n) {
            return -1;
        }

        int distance = -1;
        int[][] directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!queue.isEmpty()) {
            distance++;
            int levelSize = queue.size();
            for (int i = 0; i < levelSize; i++) {
                int[] cell = queue.poll();
                for (int[] direction : directions) {
                    int nr = cell[0] + direction[0];
                    int nc = cell[1] + direction[1];
                    if (nr >= 0 && nr < n && nc >= 0 && nc < n && grid[nr][nc] == 0) {
                        grid[nr][nc] = 1;
                        queue.offer(new int[] {nr, nc});
                    }
                }
            }
        }

        return distance;
    }
}

