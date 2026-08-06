import java.util.*;

/**
 * Algorithm:
 * Scan the grid. When a '1' is found, count a new island and DFS/BFS through
 * all connected land cells, marking them as water.
 *
 * Java data structures:
 * ArrayDeque<int[]> is used as an explicit DFS stack.
 *
 * Complexity:
 * Time O(rows * cols), space O(rows * cols) worst-case stack.
 */
class Solution {
    public int numIslands(char[][] grid) {
        if (grid == null || grid.length == 0 || grid[0].length == 0) {
            return 0;
        }
        int rows = grid.length;
        int cols = grid[0].length;
        int islands = 0;
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (grid[r][c] != '1') {
                    continue;
                }
                islands++;
                grid[r][c] = '0';
                Deque<int[]> stack = new ArrayDeque<>();
                stack.push(new int[] {r, c});
                while (!stack.isEmpty()) {
                    int[] cur = stack.pop();
                    for (int[] dir : dirs) {
                        int nr = cur[0] + dir[0];
                        int nc = cur[1] + dir[1];
                        if (0 <= nr && nr < rows && 0 <= nc && nc < cols && grid[nr][nc] == '1') {
                            grid[nr][nc] = '0';
                            stack.push(new int[] {nr, nc});
                        }
                    }
                }
            }
        }
        return islands;
    }
}

