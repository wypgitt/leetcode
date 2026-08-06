/**
 * Algorithm:
 * DFS backtracking from each cell. Match the current character, temporarily
 * mark the cell visited, search four neighbors for the next character, then
 * restore the cell.
 *
 * Java data structures:
 * int[128] counts board and word characters for the same early impossibility
 * check as the Python Counter solution.
 *
 * Complexity:
 * Worst-case O(mn * 4^L) time, O(L) recursion space.
 */
class Solution {
    private char[][] board;
    private String word;
    private int m;
    private int n;

    public boolean exist(char[][] board, String word) {
        this.board = board;
        this.word = word;
        m = board.length;
        n = board[0].length;
        int[] boardCount = new int[128];
        int[] wordCount = new int[128];
        for (char[] row : board) {
            for (char ch : row) {
                boardCount[ch]++;
            }
        }
        for (int i = 0; i < word.length(); i++) {
            wordCount[word.charAt(i)]++;
        }
        for (int i = 0; i < wordCount.length; i++) {
            if (wordCount[i] > boardCount[i]) {
                return false;
            }
        }

        for (int r = 0; r < m; r++) {
            for (int c = 0; c < n; c++) {
                if (dfs(r, c, 0)) {
                    return true;
                }
            }
        }
        return false;
    }

    private boolean dfs(int r, int c, int index) {
        if (index == word.length()) {
            return true;
        }
        if (r < 0 || r == m || c < 0 || c == n || board[r][c] != word.charAt(index)) {
            return false;
        }
        char saved = board[r][c];
        board[r][c] = '#';
        boolean found = dfs(r + 1, c, index + 1) ||
                        dfs(r - 1, c, index + 1) ||
                        dfs(r, c + 1, index + 1) ||
                        dfs(r, c - 1, index + 1);
        board[r][c] = saved;
        return found;
    }
}

