/**
 * Algorithm:
 * Same one-dimensional DP as Unique Paths, but an obstacle resets dp[c] to 0
 * because no path may stand on that cell.
 *
 * Complexity:
 * Time O(mn), space O(n).
 */
class Solution {
    public int uniquePathsWithObstacles(int[][] obstacleGrid) {
        int m = obstacleGrid.length;
        int n = obstacleGrid[0].length;
        int[] dp = new int[n];
        dp[0] = obstacleGrid[0][0] == 0 ? 1 : 0;
        for (int r = 0; r < m; r++) {
            for (int c = 0; c < n; c++) {
                if (obstacleGrid[r][c] == 1) {
                    dp[c] = 0;
                } else if (c > 0) {
                    dp[c] += dp[c - 1];
                }
            }
        }
        return dp[n - 1];
    }
}

