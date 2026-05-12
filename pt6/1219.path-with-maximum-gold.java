class Solution {
    private int[][] grid;
    private int rows;
    private int cols;
    private final int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};

    public int getMaximumGold(int[][] grid) {
        this.grid = grid;
        rows = grid.length;
        cols = grid[0].length;
        int best = 0;

        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (grid[r][c] > 0) {
                    best = Math.max(best, dfs(r, c));
                }
            }
        }

        return best;
    }

    private int dfs(int r, int c) {
        int gold = grid[r][c];
        grid[r][c] = 0;
        int bestNext = 0;

        for (int[] d : dirs) {
            int nr = r + d[0];
            int nc = c + d[1];
            if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] > 0) {
                bestNext = Math.max(bestNext, dfs(nr, nc));
            }
        }

        grid[r][c] = gold;
        return gold + bestNext;
    }
}

/*
Explanation

Try DFS backtracking from every gold cell. During one path, temporarily set the
current cell to 0 to mark it visited, explore neighbors, and restore the value
before returning.

Backtracking is necessary because a greedy next step can block a better full
path. The grid itself serves as the visited structure, avoiding a separate
boolean matrix.

Edge cases: all-zero grid returns 0; isolated gold cells are valid paths; the
best path may start from any nonzero cell.

Time complexity: exponential in the number of gold cells, commonly bounded as
O(g * 3^g) after the first move.
Space complexity: O(g) recursion depth.
*/
