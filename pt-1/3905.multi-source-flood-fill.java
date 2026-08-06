/*
 * @lc app=leetcode id=3905 lang=java
 *
 * [3905] Multi-Source Flood Fill
 *
 * Multi-source BFS expands all cells at the same distance together. If several
 * colors propose the same uncolored neighbor in a layer, keep the maximum color,
 * then commit all proposals for that time step.
 *
 * Java note: HashMap<Integer,Integer> stores proposals keyed by row*m+col.
 *
 * Time: O(nm). Space: O(nm).
 */

import java.util.ArrayDeque;
import java.util.HashMap;
import java.util.Map;

// @lc code=start
class Solution {
    public int[][] colorGrid(int n, int m, int[][] sources) {
        int[][] grid = new int[n][m];
        int[][] dist = new int[n][m];
        for (int r = 0; r < n; r++) {
            for (int c = 0; c < m; c++) {
                dist[r][c] = -1;
            }
        }

        ArrayDeque<int[]> queue = new ArrayDeque<>();
        for (int[] source : sources) {
            int row = source[0];
            int col = source[1];
            int color = source[2];
            grid[row][col] = color;
            dist[row][col] = 0;
            queue.offer(new int[] {row, col});
        }

        int[][] directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        int time = 0;
        while (!queue.isEmpty()) {
            Map<Integer, Integer> proposals = new HashMap<>();
            int layerSize = queue.size();
            for (int i = 0; i < layerSize; i++) {
                int[] cell = queue.poll();
                int row = cell[0];
                int col = cell[1];
                int color = grid[row][col];
                for (int[] dir : directions) {
                    int nr = row + dir[0];
                    int nc = col + dir[1];
                    if (0 <= nr && nr < n && 0 <= nc && nc < m && dist[nr][nc] == -1) {
                        int key = nr * m + nc;
                        proposals.put(key, Math.max(proposals.getOrDefault(key, 0), color));
                    }
                }
            }

            time++;
            for (Map.Entry<Integer, Integer> entry : proposals.entrySet()) {
                int key = entry.getKey();
                int row = key / m;
                int col = key % m;
                if (dist[row][col] == -1) {
                    dist[row][col] = time;
                    grid[row][col] = entry.getValue();
                    queue.offer(new int[] {row, col});
                }
            }
        }
        return grid;
    }
}
// @lc code=end
