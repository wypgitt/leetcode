import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    private int[][] grid;
    private int rows;
    private int cols;
    private final int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    public int closedIsland(int[][] grid) {
        this.grid = grid;
        rows = grid.length;
        cols = grid[0].length;

        for (int r = 0; r < rows; r++) {
            if (grid[r][0] == 0) {
                flood(r, 0);
            }
            if (grid[r][cols - 1] == 0) {
                flood(r, cols - 1);
            }
        }
        for (int c = 0; c < cols; c++) {
            if (grid[0][c] == 0) {
                flood(0, c);
            }
            if (grid[rows - 1][c] == 0) {
                flood(rows - 1, c);
            }
        }

        int count = 0;
        for (int r = 1; r < rows - 1; r++) {
            for (int c = 1; c < cols - 1; c++) {
                if (grid[r][c] == 0) {
                    count++;
                    flood(r, c);
                }
            }
        }

        return count;
    }

    private void flood(int r, int c) {
        Deque<int[]> stack = new ArrayDeque<>();
        stack.push(new int[] {r, c});
        grid[r][c] = 1;

        while (!stack.isEmpty()) {
            int[] cell = stack.pop();
            for (int[] d : dirs) {
                int nr = cell[0] + d[0];
                int nc = cell[1] + d[1];
                if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] == 0) {
                    grid[nr][nc] = 1;
                    stack.push(new int[] {nr, nc});
                }
            }
        }
    }
}

/*
Explanation

Land is 0 and water is 1. First flood-fill every land component touching the
border because it cannot be closed. Then scan the interior; each remaining land
component is one closed island.

The grid itself is the visited structure by changing 0 to 1. An ArrayDeque
stack avoids deep recursion.

Edge cases: border-connected land is excluded; diagonal contact does not join
islands; all-water grids return 0.

Time complexity: O(mn).
Space complexity: O(mn) worst-case stack.
*/
