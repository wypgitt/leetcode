import java.util.*;

class Solution {
    private int[] suffix;
    private int[][] memo;
    private int n;

    public int stoneGameII(int[] piles) {
        n = piles.length;
        suffix = new int[n + 1];
        for (int i = n - 1; i >= 0; i--) {
            suffix[i] = suffix[i + 1] + piles[i];
        }

        memo = new int[n][n + 1];
        for (int[] row : memo) {
            Arrays.fill(row, -1);
        }
        return bestFrom(0, 1);
    }

    private int bestFrom(int index, int m) {
        if (index >= n) {
            return 0;
        }
        if (2 * m >= n - index) {
            return suffix[index];
        }
        if (memo[index][m] != -1) {
            return memo[index][m];
        }

        int best = 0;
        for (int x = 1; x <= 2 * m; x++) {
            int opponent = bestFrom(index + x, Math.max(m, x));
            best = Math.max(best, suffix[index] - opponent);
        }
        memo[index][m] = best;
        return best;
    }
}

