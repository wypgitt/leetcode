/**
 * Algorithm:
 * Repeatedly mark horizontal and vertical runs of at least three equal nonzero
 * candies, crush them, and let each column fall by compacting non-crushed cells
 * downward. Stop when a pass marks nothing.
 *
 * Java data structures:
 * A boolean matrix records the cells to crush in the current pass.
 *
 * Complexity:
 * Each pass scans O(mn). The number of passes is bounded by the number of
 * crush events, so worst-case O((mn)^2), space O(mn).
 */
class Solution {
    public int[][] candyCrush(int[][] board) {
        int m = board.length;
        int n = board[0].length;
        boolean changed = true;
        while (changed) {
            changed = false;
            boolean[][] crush = new boolean[m][n];

            for (int r = 0; r < m; r++) {
                int c = 0;
                while (c < n) {
                    int c2 = c + 1;
                    while (c2 < n && Math.abs(board[r][c2]) == Math.abs(board[r][c])) {
                        c2++;
                    }
                    if (board[r][c] != 0 && c2 - c >= 3) {
                        changed = true;
                        for (int x = c; x < c2; x++) {
                            crush[r][x] = true;
                        }
                    }
                    c = c2;
                }
            }

            for (int c = 0; c < n; c++) {
                int r = 0;
                while (r < m) {
                    int r2 = r + 1;
                    while (r2 < m && Math.abs(board[r2][c]) == Math.abs(board[r][c])) {
                        r2++;
                    }
                    if (board[r][c] != 0 && r2 - r >= 3) {
                        changed = true;
                        for (int x = r; x < r2; x++) {
                            crush[x][c] = true;
                        }
                    }
                    r = r2;
                }
            }

            if (!changed) {
                break;
            }

            for (int c = 0; c < n; c++) {
                int write = m - 1;
                for (int r = m - 1; r >= 0; r--) {
                    if (!crush[r][c]) {
                        board[write][c] = board[r][c];
                        write--;
                    }
                }
                for (int r = write; r >= 0; r--) {
                    board[r][c] = 0;
                }
            }
        }
        return board;
    }
}

