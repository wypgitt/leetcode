import java.util.*;

/**
 * Algorithm:
 * Any 'O' connected to the border cannot be captured. BFS from border 'O'
 * cells and mark them safe as 'S'. Then flip remaining 'O' to 'X' and restore
 * safe cells back to 'O'.
 *
 * Java data structures:
 * ArrayDeque<int[]> is the BFS queue of board coordinates.
 *
 * Complexity:
 * Time O(rows * cols), space O(rows * cols) worst-case queue.
 */
class Solution {
    public void solve(char[][] board) {
        if (board == null || board.length == 0 || board[0].length == 0) {
            return;
        }
        int rows = board.length;
        int cols = board[0].length;
        Queue<int[]> q = new ArrayDeque<>();
        for (int r = 0; r < rows; r++) {
            mark(board, q, r, 0);
            mark(board, q, r, cols - 1);
        }
        for (int c = 0; c < cols; c++) {
            mark(board, q, 0, c);
            mark(board, q, rows - 1, c);
        }
        int[][] dirs = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!q.isEmpty()) {
            int[] cur = q.poll();
            for (int[] dir : dirs) {
                int nr = cur[0] + dir[0];
                int nc = cur[1] + dir[1];
                if (0 <= nr && nr < rows && 0 <= nc && nc < cols && board[nr][nc] == 'O') {
                    board[nr][nc] = 'S';
                    q.offer(new int[] {nr, nc});
                }
            }
        }
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                if (board[r][c] == 'O') {
                    board[r][c] = 'X';
                } else if (board[r][c] == 'S') {
                    board[r][c] = 'O';
                }
            }
        }
    }

    private void mark(char[][] board, Queue<int[]> q, int r, int c) {
        if (board[r][c] == 'O') {
            board[r][c] = 'S';
            q.offer(new int[] {r, c});
        }
    }
}

