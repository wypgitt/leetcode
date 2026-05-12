import java.util.ArrayDeque;
import java.util.Queue;

/*
 * LeetCode 1391 - Check if There is a Valid Path in a Grid
 */
class Solution {
    private static final int[][][] DIRECTIONS = {
            {},
            {{0, -1}, {0, 1}},
            {{-1, 0}, {1, 0}},
            {{0, -1}, {1, 0}},
            {{0, 1}, {1, 0}},
            {{0, -1}, {-1, 0}},
            {{0, 1}, {-1, 0}}
    };

    public boolean hasValidPath(int[][] grid) {
        int rows = grid.length;
        int cols = grid[0].length;
        boolean[][] seen = new boolean[rows][cols];
        Queue<int[]> queue = new ArrayDeque<>();

        queue.offer(new int[] {0, 0});
        seen[0][0] = true;

        while (!queue.isEmpty()) {
            int[] cell = queue.poll();
            int row = cell[0];
            int col = cell[1];

            if (row == rows - 1 && col == cols - 1) {
                return true;
            }

            for (int[] direction : DIRECTIONS[grid[row][col]]) {
                int nextRow = row + direction[0];
                int nextCol = col + direction[1];

                if (nextRow < 0 || nextRow >= rows || nextCol < 0 || nextCol >= cols) {
                    continue;
                }
                if (seen[nextRow][nextCol]) {
                    continue;
                }
                if (!connectsBack(grid[nextRow][nextCol], -direction[0], -direction[1])) {
                    continue;
                }

                seen[nextRow][nextCol] = true;
                queue.offer(new int[] {nextRow, nextCol});
            }
        }

        return false;
    }

    private boolean connectsBack(int streetType, int dr, int dc) {
        for (int[] direction : DIRECTIONS[streetType]) {
            if (direction[0] == dr && direction[1] == dc) {
                return true;
            }
        }
        return false;
    }
}

/*
 * Interview explanation
 * ---------------------
 * Algorithm:
 * Model cells as graph nodes. A move is valid only when the current street has
 * an exit in that direction and the neighboring street has an entrance back.
 * BFS from the top-left checks whether the bottom-right is reachable.
 *
 * Java data structures:
 * `int[][][] DIRECTIONS` maps street type to allowed movement deltas.
 * `Queue<int[]>` performs BFS and `boolean[][] seen` prevents cycles.
 *
 * Edge cases:
 * - 1x1 grid returns true because start equals destination.
 * - Direction mismatch is rejected by `connectsBack`.
 * - Cycles are safe because visited cells are not enqueued again.
 *
 * Complexity:
 * Time O(mn).
 * Space O(mn).
 */
