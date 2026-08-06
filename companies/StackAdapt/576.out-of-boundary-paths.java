import java.util.*;

/**
 * Algorithm:
 * Memoized DFS counts paths from (row, col, moves). Stepping outside the grid
 * contributes one path; running out of moves inside contributes zero.
 *
 * Java data structures:
 * A 3D Integer array stores nullable memoized values, matching Python's
 * lru_cache behavior for the bounded state space.
 *
 * Complexity:
 * Time O(m * n * maxMove), space O(m * n * maxMove).
 */
class Solution {
    private static final int MOD = 1_000_000_007;
    private int m;
    private int n;
    private Integer[][][] memo;

    public int findPaths(int m, int n, int maxMove, int startRow, int startColumn) {
        this.m = m;
        this.n = n;
        this.memo = new Integer[m][n][maxMove + 1];
        return dp(startRow, startColumn, maxMove);
    }

    private int dp(int r, int c, int moves) {
        if (r < 0 || r >= m || c < 0 || c >= n) {
            return 1;
        }
        if (moves == 0) {
            return 0;
        }
        if (memo[r][c][moves] != null) {
            return memo[r][c][moves];
        }
        long total = 0;
        total += dp(r + 1, c, moves - 1);
        total += dp(r - 1, c, moves - 1);
        total += dp(r, c + 1, moves - 1);
        total += dp(r, c - 1, moves - 1);
        memo[r][c][moves] = (int) (total % MOD);
        return memo[r][c][moves];
    }
}

