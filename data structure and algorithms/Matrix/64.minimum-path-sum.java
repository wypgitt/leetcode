/**
 * Algorithm:
 * One-dimensional DP over rows. The minimum cost to a cell is its value plus
 * min(cost from above, cost from left), with special handling for first row and
 * first column.
 *
 * Complexity:
 * Time O(mn), space O(n).
 */
class Solution {
    public int minPathSum(int[][] grid) {
        int m = grid.length;
        int n = grid[0].length;
        int[] dp = new int[n];
        for (int r = 0; r < m; r++) {
            for (int c = 0; c < n; c++) {
                if (r == 0 && c == 0) {
                    dp[c] = grid[r][c];
                } else if (r == 0) {
                    dp[c] = dp[c - 1] + grid[r][c];
                } else if (c == 0) {
                    dp[c] += grid[r][c];
                } else {
                    dp[c] = Math.min(dp[c], dp[c - 1]) + grid[r][c];
                }
            }
        }
        return dp[n - 1];
    }
}

