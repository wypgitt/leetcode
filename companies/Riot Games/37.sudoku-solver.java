/*
 * @lc app=leetcode id=37 lang=java
 *
 * [37] Sudoku Solver
 */

/*
 * =============================================================================
 * INTERVIEW: HOW TO EXPLAIN (elevator → whiteboard)
 * =============================================================================
 *
 * 30 seconds:
 *   "Fill empty cells with backtracking: try digits 1–9, recurse to the next
 *   cell, undo if we hit a dead end. Track which digits appear in each row,
 *   column, and 3×3 box with bitmasks for O(1) legality checks."
 *
 * Algorithm: DFS over cell index 0..80 in row-major order. For '.', try each
 * digit not present in row | col | box masks; on success propagate; else XOR
 * bits back and restore '.'.
 *
 * Time: exponential worst case; practical for 9×9 with pruning. Space: O(1)
 * extra beyond recursion stack (fixed 81).
 * =============================================================================
 */

// @lc code=start
class Solution {
    /**
     * Solve the board in place. {@code board[r][c]} is {@code '.'} or {@code '1'}..{@code '9'}.
     */
    public void solveSudoku(char[][] board) {
        int[] rows = new int[9];
        int[] cols = new int[9];
        int[] boxes = new int[9];

        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                char ch = board[r][c];
                if (ch == '.') {
                    continue;
                }
                int bit = 1 << (ch - '1');
                int b = (r / 3) * 3 + (c / 3);
                rows[r] |= bit;
                cols[c] |= bit;
                boxes[b] |= bit;
            }
        }

        dfs(board, rows, cols, boxes, 0);
    }

    private boolean dfs(char[][] board, int[] rows, int[] cols, int[] boxes, int cell) {
        if (cell == 81) {
            return true;
        }
        int r = cell / 9;
        int c = cell % 9;
        if (board[r][c] != '.') {
            return dfs(board, rows, cols, boxes, cell + 1);
        }

        int b = (r / 3) * 3 + (c / 3);
        int used = rows[r] | cols[c] | boxes[b];

        for (int d = 0; d < 9; d++) {
            int bit = 1 << d;
            if ((used & bit) != 0) {
                continue;
            }

            board[r][c] = (char) ('1' + d);
            rows[r] |= bit;
            cols[c] |= bit;
            boxes[b] |= bit;

            if (dfs(board, rows, cols, boxes, cell + 1)) {
                return true;
            }

            rows[r] ^= bit;
            cols[c] ^= bit;
            boxes[b] ^= bit;
            board[r][c] = '.';
        }
        return false;
    }
}
// @lc code=end
